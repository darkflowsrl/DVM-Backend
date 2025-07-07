from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import uvicorn
from threading import Thread
import time

from src.can_bus import (
    reader_loop,
    write_on_bus_all_rpm,
    write_on_bus_test,
    write_on_bus_take_status,
    write_on_bus_take_rpm,
    write_on_bus_all_config,
    write_scan_boards,
    write_on_bus_rename,
    write_on_bus_factory_reset,
    write_on_bus_get_interface_version,
    write_on_ask_caudalimetro,
    buffer,
    port_config,
    BOARD_VERSION,
    available_boards_from_scan
)
from src.canbus_parser import BoardParams, BoardTest, NodeConfiguration
from src.log import log

# Constants and global state
VERSION: str = "1.3.0"
HOST: str = "0.0.0.0"
PORT: int = 8080

LAST_RPM = {"rpm1": 0, "rpm2": 0, "rpm3": 0, "rpm4": 0}
node_list: list = []

app = FastAPI()

def get_status() -> None:
    """Background thread: periodically request status from all nodes."""
    while True:
        try:
            time.sleep(1)
            for node in node_list:
                write_on_bus_take_status(bus_config=port_config, params=BoardTest(node))
            # También solicitar datos del caudalímetro para todos los nodos
            write_on_ask_caudalimetro(bus_config=port_config, boards=node_list)
        except Exception as e:
            print(f"Exception in get_status: {e}")

def get_rmp() -> None:
    """Background thread: periodically request RPM data from all nodes."""
    while True:
        time.sleep(1)
        try:
            for node in node_list:
                write_on_bus_take_rpm(bus_config=port_config, params=BoardTest(int(node)))
        except Exception as e:
            print(f"Exception in get_rmp: {e}")

@app.post("/testing")
def testing_endpoint(payload: dict = Body(...)):
    """Endpoint to send test command to specified nodes."""
    nodos = payload.get("nodos", [])
    for node_id in nodos:
        write_on_bus_test(bus_config=port_config, params=BoardTest(node_id))
    return {"status": "ok"}

@app.post("/normal")
def normal_endpoint(payload: dict = Body(...)):
    """Endpoint to send normal operation RPM values to specified nodes."""
    global LAST_RPM
    nodos = payload.get("nodos", [])
    for nodo in nodos:
        # Si todas las RPM son 0, enviar directamente ceros
        if (nodo.get("rpm1") == 0 and nodo.get("rpm2") == 0 and nodo.get("rpm3") == 0 and nodo.get("rpm4") == 0):
            write_on_bus_all_rpm(bus_config=port_config, params=BoardParams(nodo["nodo"], 0, 0, 0, 0))
            continue
        # Cambio gradual de RPM (arranque/paro suave)
        write_on_bus_all_rpm(bus_config=port_config, params=BoardParams(
            nodo["nodo"], nodo["rpm1"], LAST_RPM["rpm2"], LAST_RPM["rpm3"], LAST_RPM["rpm4"]
        ))
        time.sleep(0.1)
        write_on_bus_all_rpm(bus_config=port_config, params=BoardParams(
            nodo["nodo"], nodo["rpm1"], nodo["rpm2"], LAST_RPM["rpm3"], LAST_RPM["rpm4"]
        ))
        time.sleep(0.1)
        write_on_bus_all_rpm(bus_config=port_config, params=BoardParams(
            nodo["nodo"], nodo["rpm1"], nodo["rpm2"], nodo["rpm3"], LAST_RPM["rpm4"]
        ))
        time.sleep(0.1)
        write_on_bus_all_rpm(bus_config=port_config, params=BoardParams(
            nodo["nodo"], nodo["rpm1"], nodo["rpm2"], nodo["rpm3"], nodo["rpm4"]
        ))
        # Actualizar últimas RPM registradas para el próximo ajuste suave
        LAST_RPM["rpm1"] = nodo["rpm1"]
        LAST_RPM["rpm2"] = nodo["rpm2"]
        LAST_RPM["rpm3"] = nodo["rpm3"]
        LAST_RPM["rpm4"] = nodo["rpm4"]
    return {"status": "ok"}

@app.post("/setConfiguracion")
def set_configuracion_endpoint(payload: dict = Body(...)):
    """Endpoint to send configuration parameters to specified nodes."""
    configuraciones = payload.get("configuraciones", [])
    for conf in configuraciones:
        nodo_conf = NodeConfiguration(conf["nodo"],
                                      conf["variacionRPM"],
                                      conf["subcorriente"],
                                      conf["sobrecorriente"],
                                      conf["cortocicuito"],
                                      conf["sensor"],
                                      conf["electrovalvula"])
        write_on_bus_all_config(bus_config=port_config, node=nodo_conf)
    return {"status": "ok"}

@app.get("/scan")
def scan_endpoint():
    """Endpoint to scan the CAN bus for connected boards."""
    write_scan_boards(bus_config=port_config)
    time.sleep(2)  # Esperar a que finalice el escaneo
    global node_list
    node_list.extend(available_boards_from_scan)
    node_list = list(set(node_list))
    return {"nodos": available_boards_from_scan}

@app.post("/renombrar")
def renombrar_endpoint(payload: dict = Body(...)):
    """Endpoint to rename a node (assign a new ID)."""
    old_id = payload.get("nodo")
    new_id = payload.get("nodoNombreNuevo")
    if old_id is None or new_id is None:
        return JSONResponse(status_code=400, content={"error": "Falta 'nodo' o 'nodoNombreNuevo'"})
    write_on_bus_rename(bus_config=port_config,
                        b1=BoardParams(old_id, 0, 0, 0, 0),
                        b2=BoardParams(new_id, 0, 0, 0, 0))
    # Actualizar la lista de nodos conocidos
    if old_id in node_list:
        node_list.remove(old_id)
    node_list.append(new_id)
    node_list = list(set(node_list))
    return {"status": "ok"}

@app.post("/restablecerFabrica")
def restablecer_fabrica_endpoint(payload: dict = Body(...)):
    """Endpoint to reset a node to factory settings."""
    nodo_id = payload.get("nodo")
    if nodo_id is None:
        return JSONResponse(status_code=400, content={"error": "Falta 'nodo'"})
    write_on_bus_factory_reset(bus_config=port_config, params=BoardParams(nodo_id, 0, 0, 0, 0))
    return {"status": "ok"}

@app.get("/version")
def version_endpoint():
    """Endpoint to obtain system and board version information."""
    board_version = BOARD_VERSION  # Use latest known board version
    return {"version": VERSION, "boardVersion": board_version}

@app.get("/datosMeteorologicos")
def datos_meteorologicos_endpoint():
    """Endpoint to get current meteorological data."""
    data = buffer.parse_meteor()
    if isinstance(data, dict) and "command" in data:
        data.pop("command")
    return data

@app.get("/estadoGeneralNodos")
def estado_general_nodos_endpoint():
    """Endpoint to get current general status of nodes."""
    data = buffer.parse_node()
    if isinstance(data, dict) and "command" in data:
        data.pop("command")
    return data

@app.on_event("startup")
def startup_event():
    """Initialize background tasks and CAN interface on startup."""
    # Iniciar hilos de fondo para leer del bus CAN y solicitar datos periódicamente
    Thread(target=reader_loop, args=(port_config,), daemon=True).start()
    Thread(target=get_rmp, daemon=True).start()
    Thread(target=get_status, daemon=True).start()
    # Solicitar versión de interfaz de placas al iniciar (para obtener BOARD_VERSION)
    try:
        write_on_bus_get_interface_version(bus_config=port_config)
    except Exception as e:
        log(f"Error al obtener versión de interfaz: {e}", "startup_event")
    log("La API FastAPI se inició satisfactoriamente.", "startup_event")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

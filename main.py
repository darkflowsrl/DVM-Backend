from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any
from threading import Thread
import uvicorn
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

VERSION: str = "1.3.0"
LAST_RPM = {"rpm1": 0, "rpm2": 0, "rpm3": 0, "rpm4": 0}
node_list: list[int] = []

# API metadata for Swagger
app = FastAPI(
    title="DVM CAN Bus Control API",
    version=VERSION,
    description="API para gestión y monitoreo de nodos en bus CAN mediante DVM-Scripts"
)

# ----- Pydantic Models -----
class StatusResponse(BaseModel):
    status: str = Field(..., description="Estado de la operación")

class TestingPayload(BaseModel):
    nodos: list[int] = Field(..., description="Lista de IDs de nodos a los que enviar comando de prueba")

class NormalNode(BaseModel):
    nodo: int = Field(..., description="ID del nodo")
    rpm1: int = Field(..., ge=0, description="RPM motor 1")
    rpm2: int = Field(..., ge=0, description="RPM motor 2")
    rpm3: int = Field(..., ge=0, description="RPM motor 3")
    rpm4: int = Field(..., ge=0, description="RPM motor 4")

class NormalPayload(BaseModel):
    nodos: list[NormalNode] = Field(..., description="Parámetros de RPM para cada nodo")

class ConfigItem(BaseModel):
    nodo: int = Field(..., description="ID del nodo a configurar")
    variacionRPM: int = Field(..., description="Variación de RPM")
    subcorriente: float = Field(..., description="Umbral de subcorriente")
    sobrecorriente: float = Field(..., description="Umbral de sobrecorriente")
    cortocicuito: float = Field(..., description="Umbral de cortocircuito")
    sensor: int = Field(..., description="Configuración de sensor")
    electrovalvula: int = Field(..., description="Configuración de electroválvula")

class ConfigPayload(BaseModel):
    configuraciones: list[ConfigItem] = Field(..., description="Lista de configuraciones por nodo")

class RenamePayload(BaseModel):
    nodo: int = Field(..., description="ID actual del nodo")
    nodoNombreNuevo: int = Field(..., description="Nuevo ID del nodo")

class FactoryResetPayload(BaseModel):
    nodo: int = Field(..., description="ID del nodo a restablecer a fábrica")

class ScanResponse(BaseModel):
    nodos: list[int] = Field(..., description="Lista de nodos detectados en el escaneo del bus CAN")

class VersionResponse(BaseModel):
    version: str = Field(..., description="Versión de la API")
    boardVersion: str = Field(..., description="Versión de firmware de la interfaz CAN")

class MeteorResponse(BaseModel):
    temperatura: float = Field(..., description="Temperatura ambiente")
    humedad: float = Field(..., description="Humedad relativa")
    presion: float = Field(..., description="Presión atmosférica")

class NodeStateResponse(BaseModel):
    nodo: int = Field(..., description="ID del nodo")
    state1: Any = Field(..., description="Estado 1 del nodo")
    state2: Any = Field(..., description="Estado 2 del nodo")
    state3: Any = Field(..., description="Estado 3 del nodo")
    state4: Any = Field(..., description="Estado 4 del nodo")
    voltaje: float = Field(..., description="Voltaje medido en el nodo (V)")

# ----- Background Tasks -----
def get_status() -> None:
    """Hilo: solicitar estado de nodos y caudalímetro cada segundo"""
    while True:
        try:
            time.sleep(1)
            for node in node_list:
                write_on_bus_take_status(bus_config=port_config, params=BoardTest(node))
            write_on_ask_caudalimetro(bus_config=port_config, boards=node_list)
        except Exception as e:
            print(f"Exception in get_status: {e}")


def get_rmp() -> None:
    """Hilo: solicitar datos de RPM cada segundo"""
    while True:
        time.sleep(1)
        try:
            for node in node_list:
                write_on_bus_take_rpm(bus_config=port_config, params=BoardTest(node))
        except Exception as e:
            print(f"Exception in get_rmp: {e}")

# ----- Endpoints -----
@app.post("/testing", response_model=StatusResponse)
def testing_endpoint(payload: TestingPayload = Body(...)):
    """
    Envía un comando de prueba a los nodos especificados.
    - **nodos**: lista de IDs de nodos.
    """
    for node_id in payload.nodos:
        write_on_bus_test(bus_config=port_config, params=BoardTest(node_id))
    return StatusResponse(status="ok")

@app.post("/normal", response_model=StatusResponse)
def normal_endpoint(payload: NormalPayload = Body(...)):
    """
    Establece valores de RPM para operación normal.
    - **nodos**: lista de objetos con 'nodo', 'rpm1'...'rpm4'.
    """
    global LAST_RPM
    for nodo in payload.nodos:
        if all(getattr(nodo, f"rpm{i}") == 0 for i in range(1,5)):
            write_on_bus_all_rpm(bus_config=port_config,
                                 params=BoardParams(nodo.nodo, 0,0,0,0))
            continue
        sequence = []
        for i in range(1,5):
            values = [nodo.rpm1, nodo.rpm2, nodo.rpm3, nodo.rpm4]
            for j in range(4):
                if j < i:
                    values[j] = getattr(nodo, f"rpm{j+1}")
                else:
                    values[j] = LAST_RPM[f"rpm{j+1}"]
            sequence.append(values.copy())
        for seq in sequence:
            write_on_bus_all_rpm(bus_config=port_config,
                                 params=BoardParams(nodo.nodo, *seq))
            time.sleep(0.1)
        LAST_RPM.update({f"rpm{i}": getattr(nodo, f"rpm{i}") for i in range(1,5)})
    return StatusResponse(status="ok")

@app.post("/setConfiguracion", response_model=StatusResponse)
def set_configuracion_endpoint(payload: ConfigPayload = Body(...)):
    """
    Envía parámetros de configuración a los nodos.
    - **configuraciones**: lista de configuraciones (variacionRPM, subcorriente, etc.).
    """
    for conf in payload.configuraciones:
        nodo_conf = NodeConfiguration(
            conf.nodo, conf.variacionRPM, conf.subcorriente,
            conf.sobrecorriente, conf.cortocicuito,
            conf.sensor, conf.electrovalvula
        )
        write_on_bus_all_config(bus_config=port_config, node=nodo_conf)
    return StatusResponse(status="ok")

@app.get("/scan", response_model=ScanResponse)
def scan_endpoint():
    """Escanea el bus CAN y retorna lista de nodos detectados."""
    write_scan_boards(bus_config=port_config)
    time.sleep(2)
    global node_list
    node_list = list(set(node_list + available_boards_from_scan))
    return ScanResponse(nodos=available_boards_from_scan)

@app.post("/renombrar", response_model=StatusResponse)
def renombrar_endpoint(payload: RenamePayload = Body(...)):
    """
    Renombra un nodo existente.
    - **nodo**: ID actual.
    - **nodoNombreNuevo**: nuevo ID.
    """
    if payload.nodo not in node_list:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    write_on_bus_rename(bus_config=port_config,
                        b1=BoardTest(payload.nodo),
                        b2=BoardTest(payload.nodoNombreNuevo))
    node_list.remove(payload.nodo)
    node_list.append(payload.nodoNombreNuevo)
    return StatusResponse(status="ok")

@app.post("/restablecerFabrica", response_model=StatusResponse)
def restablecer_fabrica_endpoint(payload: FactoryResetPayload = Body(...)):
    """
    Restablece la configuración de fábrica de un nodo.
    - **nodo**: ID del nodo.
    """
    write_on_bus_factory_reset(bus_config=port_config,
                                params=BoardTest(payload.nodo))
    return StatusResponse(status="ok")

@app.get("/version", response_model=VersionResponse)
def version_endpoint():
    """Retorna versiones de la API y de las placas."""
    return VersionResponse(version=VERSION, boardVersion=BOARD_VERSION)

@app.get("/datosMeteorologicos", response_model=MeteorResponse)
def datos_meteorologicos_endpoint():
    """Retorna datos meteorológicos actuales sin campo 'command'."""
    data = buffer.parse_meteor()
    data.pop("command", None)
    return MeteorResponse(**data)

@app.get("/estadoGeneralNodos", response_model=list[NodeStateResponse])
def estado_general_nodos_endpoint():
    """Retorna estado general de los nodos sin campo 'command'."""
    data = buffer.parse_node()
    data.pop("command", None)
    # Suponer que data es lista de dicts con campos compatibles
    
    return [NodeStateResponse(**node) for node in data["nodos"]]

@app.on_event("startup")
def startup_event():
    """Inicializa hilos de lectura y solicita versión de interfaz."""
    Thread(target=reader_loop, args=(port_config,), daemon=True).start()
    Thread(target=get_rmp, daemon=True).start()
    Thread(target=get_status, daemon=True).start()
    try:
        write_on_bus_get_interface_version(bus_config=port_config)
    except Exception as e:
        log(f"Error al obtener versión de interfaz: {e}", "startup_event")
    log("La API FastAPI se inició satisfactoriamente.", "startup_event")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

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
    buffer,
    port_config,
    available_boards_from_scan
    )
from src.canbus_parser import *
from src.log import log
from threading import Thread
from typing import List
from time import sleep
import sys
import socket
import json
import time

""" 
Los siguientes comandos de linux sirven para levantar la interfaz can0
desde el hardware.
"""
IPS: List[str] = ['localhost', '192.168.1.62']
HOST: str = IPS[1]
PORT: int = 8080    
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM

sock = socket.socket(FAMILY, TYPE)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
clients: list = []
nodes: list = []

log("Se inicio el script satisfactoriamente.", 'main')

"""
DOCUMENTACIÓN:
Se propone el siguiente protocolo actualizado:
Al utilizar el socket y no utilizar comandos, para saber a que proceso
corresponde cada mensaje, se utilizará la variable command.

Protocolo de testing:
{
    command : "testing",
    nodos :  [1030, 1230, 1150]
}

Protocolo de funcionamiento normal:
{
    command : "normal",
    nodo : 1030,
    rpm1 : 2000,
    rpm2 : 2500,
    rpm3 : 1000,
    rpm4 : 0,
}
, 'send_data_over_node'
Protocolo de datos meteorológicos:
{
    command : "datosMeteorologicos",
    humedad : 78,
    velViento : 34,
    dirViento : 180,
    temperatura : 25,
    puntoDeRocio : 25
}

Protocolo de estado general del nodo:
{
    command : "estadoGeneralNodos",
    nodos: [
        {
            nodo : 1030,
            state1 : 3.1,
            state2 : 3.2,
            state3 : 3.3,
            state4 : 6.2,
            corr1 : 2000,
            corr2 : 2500,
            corr3 : 2000,
            corr4 : 500,
            rpm1 : 3.1,
            rpm2 : 3.2,
            rpm3 : 3.3,
            rpm4 : 6.2,
            voltaje : 12.8
        }
    ]
}
"""

def get_status() -> None:
    global nodes
    
    while True:
        try:
            time.sleep(1)
            print(f'Nodos -> {nodes}')
            
            for node in nodes:
                write_on_bus_take_status(bus_config=port_config,
                                params=BoardTest(node))
        except Exception as e:
            print(f'Exception at: get_status -> {str(e)}')
                        
def get_rmp() -> None:
    global nodes
    
    while True:
        nodes = list(set(nodes))
        time.sleep(1)
        try:
            for i, node in enumerate(nodes):
                write_on_bus_take_rpm(bus_config=port_config,
                                params=BoardTest(int(node)))
        except Exception as e:
            print(f'Exception at: get_rpm -> {str(e)}')
                            
def _listen_for_incomming_clients() -> None:
    global sock
    global clients
    
    sock.listen(1)
    sock.settimeout(10)  # Establecer un tiempo de espera de 10 segundos
    
    while True:
        try:
            conn, addr = sock.accept()
            log(f'Nuevo cliente conectado: {addr}', '_listen_for_incomming_clients')
            client: dict = {'conn': conn, 'addr': addr}
            clients.append(client)
            task_write_into_node = Thread(target=send_data_over_node,
                                          args=(client,),
                                          daemon=True)
            task_write_into_node.start()

        except socket.timeout:
            pass
    
def send_data_over_socket() -> None:
    global clients
    
    while True:
        if len(clients) != 0:
            for idx, client in enumerate(clients):
                try:
                    conn = client['conn']
                    data_meteor = json.dumps(buffer.parse_meteor()).encode()
                    data_node_data = json.dumps(buffer.parse_node()).encode()
                    
                    all_data: list = [data_meteor, data_node_data]
                    
                    for data in all_data:
                        log(data, 'send_data_over_socket')
                        conn.sendall(data)
                        sleep(1)
                        
                except ConnectionError as e:
                    del clients[idx]
                    log(str(e), 'send_data_over_socket')
                except OSError:
                    pass
            
def send_data_over_node(client) -> None:
    global nodes
    global available_boards_from_scan
    
    while True:
        try:
            conn: socket.socket = client["conn"]
            data = conn.recv(1024*10)
            
            data = json.loads(data)
            command: str = data["command"] 
            
            log(f'Nuevo mensaje recibido: {data}', 'send_data_over_node')
            print(f'Nuevo mensaje recibido -> {data}')
            
            if command == 'testError':
                raise Exception
            
            if command == "testing":
                nodes.extend(data["nodos"])
                for node in data["nodos"]:
                    write_on_bus_test(bus_config=port_config,
                                    params=BoardTest(node))
                    
            elif command == "normal":
                write_on_bus_all_rpm(bus_config=port_config,
                                        params=BoardParams(data["nodo"],
                                                    data["rpm1"],
                                                    data["rpm2"],
                                                    data["rpm3"],
                                                    data["rpm4"]))     
                new_node = data["nodo"]
                nodes.append(new_node)
            
            elif command == "setConfiguracion":
                for nodo in data["configuraciones"]:
                    nodo_: NodeConfiguration = NodeConfiguration(nodo['nodo'],
                                                                 nodo['variacionRPM'],
                                                                 nodo['subcorriente'],
                                                                 nodo['sobrecorriente'],
                                                                 nodo['cortocicuito'],
                                                                 nodo['sensor'],
                                                                 nodo['electrovalvula'])
                    write_on_bus_all_config(bus_config=port_config,
                                            node=nodo_)

            elif command == "scan":
                write_scan_boards(bus_config=port_config)
                
                time.sleep(2) # Sleep to wait to scan ending.
                
                data: dict = {
                    "command": "rtaScan",
                    "nodos": available_boards_from_scan
                }
                
                nodes.extend(available_boards_from_scan)
                
                data = json.dumps(data).encode()
                
                conn.sendall(data)
            
            elif command == 'renombrar':
                if data['nodo'] in available_boards_from_scan:
                    print(f'\n[DEBUG]\n Deleting -> {data["nodo"]}')
                    del(available_boards_from_scan[available_boards_from_scan.index(data['nodo'])])
                
                write_on_bus_rename(bus_config=port_config,
                                    b1=BoardParams(data['nodo'], 0, 0, 0, 0),
                                    b2=BoardParams(data['nodoNombreNuevo'], 0, 0, 0, 0))
                
            elif command == 'restablecerFabrica':
                write_on_bus_factory_reset(bus_config=port_config,
                                           params=BoardParams(data['nodo'], 0, 0, 0, 0))
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log(f'Error: {type(e).__name__}: {e}', 'send_data_over_node')
            print(f"[error] send_data_over_node -> {type(e).__name__}: {e} , {exc_obj}, line {exc_tb.tb_lineno}")
            break
    
if __name__ == '__main__':
    while True:
        task_wait_for_client = Thread(target=_listen_for_incomming_clients)
        task_read_node = Thread(target=reader_loop, args=(port_config,))
        task_write_into_front = Thread(target=send_data_over_socket)
        task_get_rpm = Thread(target=get_rmp)
        task_take_status = Thread(target=get_status)
                
        task_wait_for_client.start()
        task_read_node.start()
        task_write_into_front.start()
        task_get_rpm.start()
        task_take_status.start()
        
        task_wait_for_client.join()
        task_read_node.join()
        task_write_into_front.join()
        task_get_rpm.join()
        task_take_status.join()
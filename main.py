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
    BOARD_VERSION
    )
from src.canbus_parser import *
from src.log import log
from threading import Thread
from typing import List, Dict
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
HOST: str = IPS[0]
PORT: int = 8080    
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM
VERSION: str = '1.2.0'


LAST_RPM: Dict[str, int] = {
    "rpm1": 0,
    "rpm2": 0,
    "rpm3": 0,
    "rpm4": 0
}

sock = socket.socket(FAMILY, TYPE)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
clients: list = []

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

Nodo:
{
    nodo : 1030,
    rpm1 : 2000,
    rpm2 : 2500,
    rpm3 : 1000,
    rpm4 : 0,
}

Protocolo de funcionamiento normal:
{
    command : "normal",
    nodos : List[Nodo]
}

GPSData
{
    nroSatelites : Int,
    velocicidad : Float,
    latitud : Float,
    longitud : Float,
    altura : Float
}

caudalBoards
{
    board_id : Int,
    caudalEngine0 : Float,
    caudalEngine1 : Float,
    caudalEngine2 : Float,
    caudalEngine3 : Float
}

caudalData
{
    boards : List[caudalBoards]
}

Protocolo de datos meteorológicos:
{
    command : "datosMeteorologicos",
    humedad : Float,
    velViento : Float,
    dirViento : Float,
    temperatura : Float,
    puntoDeRocio : Float,
    presionAtmosferica : Float
    gpsInfo : GPSData,
    caudalInfo : caudalData
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

node_list: list = []


def get_status() -> None:
    while True:
        try:
            time.sleep(1)
            
            for node in node_list:
                write_on_bus_take_status(bus_config=port_config,
                                params=BoardTest(node))
                
            """
            With the purpose of not open another Thread
            I will create a new process here.
            TEST THIS
            """
            write_on_ask_caudalimetro(bus_config=port_config,
                                      boards=node_list)
            
        except Exception as e:
            print(f'Exception at: get_status -> {str(e)}')
                        
def get_rmp() -> None:
    while True:
        time.sleep(1)
        try:
            for _, node in enumerate(node_list):
                write_on_bus_take_rpm(bus_config=port_config,
                                params=BoardTest(int(node)))
        except Exception as e:
            print(f'Exception at: get_rpm -> {str(e)}')
                            
def _listen_for_incomming_clients() -> None:
    """
    Initialization:
        The function retrieves the sock object which represents the server socket.
        It retrieves the clients list which contains information about connected clients.
        It sets a timeout of 10 seconds for accepting connections.
    
    Listening Loop:
        The function enters an infinite loop to continuously listen for incoming connections.
        Inside the loop, it attempts to accept a new connection using sock.accept().
        If a connection is accepted, it retrieves the client's connection object (conn) and address (addr).
        The function logs a message indicating that a new client has connected.
        It creates a new dictionary client containing the connection object and address.
        It appends the client dictionary to the clients list.
        The function creates a new thread called task_write_into_node to handle communication with the connected client.
        The thread is started with the client dictionary as an argument.
    
    Timeout Handling:
        If a socket.timeout exception occurs, the loop continues without accepting a connection.
    """
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
    """
    Initialization:
        The function retrieves the clients list which contains information about connected clients.
        It enters an infinite loop to continuously send data to clients.
    
    Client Loop:
        The function iterates through the clients list.
        For each client, it attempts to send data using the client's conn (connection) object.
        The data to be sent is retrieved from the buffer object using the parse_meteor and parse_node methods. These methods return dictionaries containing meteorological data and node data, respectively.
        The data is then converted to JSON format using json.dumps and encoded using encode.
        The encoded data is sent to the client using conn.sendall.
        The function sleeps for 1 second after sending data to each client.
    
    Error Handling:
        The function includes a try-except block to handle any exceptions that may occur during data sending.
        If a ConnectionError occurs, the client is removed from the clients list and the error message is logged.
        If an OSError occurs, the error is simply logged and the loop continues.
    
    Loop Termination:
        The loop continues until all clients have disconnected or an error occurs.
        Additional Notes:
        This function relies on the buffer object and the parse_meteor and parse_node methods defined in other files.
        The function uses the log function from the src.log module for logging messages.
        The function uses threads to handle communication with multiple clients concurrently.
    """
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
    """
    Initialization:
        It retrieves the node_list which contains the IDs of all connected nodes.
        It sends a message to the bus to get the interface version of the connected boards.
        
    Main Loop:
        The function enters an infinite loop to continuously receive and process data from the client.
        Inside the loop, it attempts to receive data from the client using conn.recv(1024*10).
        If data is received, it is parsed as JSON using json.loads(data).
        The function then extracts the command field from the received data.
    
    Command Handling:
        Based on the received command, the function performs different actions:
        testError: Raises an exception to test error handling.
        testing: Iterates through the nodos list in the received data and sends a test message to each node using write_on_bus_test.
        normal: Iterates through the nodos list and sends RPM values to each node using write_on_bus_all_rpm.
        setConfiguracion: Iterates through the configuraciones list and sends configuration parameters to each node using write_on_bus_all_config.
        scan: Sends a scan message to the bus using write_scan_boards, waits for 2 seconds, retrieves the list of available boards from available_boards_from_scan, updates the node_list, and sends a response to the client with the list of available boards.
        renombrar: Sends a rename message to the bus using write_on_bus_rename with the old and new node IDs.
        restablecerFabrica: Sends a factory reset message to the bus using write_on_bus_factory_reset with the node ID.
    """
    global node_list
    
    # Get board version
    write_on_bus_get_interface_version(bus_config=port_config)
    
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
                for node in data["nodos"]:
                    write_on_bus_test(bus_config=port_config,
                                    params=BoardTest(node))
                    
            elif command == "normal":
                for nodo in data["nodos"]:
                    if nodo['rpm1'] == 0 and nodo['rpm2'] == 0 and nodo['rpm3'] == 0 and nodo['rpm4'] == 0:
                        write_on_bus_all_rpm(bus_config=port_config,
                                                params=BoardParams(nodo["nodo"],
                                                            0,
                                                            0,
                                                            0,
                                                            0))
                        continue
                    # Smooth start
                    write_on_bus_all_rpm(bus_config=port_config,
                                            params=BoardParams(nodo["nodo"],
                                                        nodo["rpm1"],
                                                        LAST_RPM['rpm2'],
                                                        LAST_RPM['rpm3'],
                                                        LAST_RPM['rpm4']))
                    time.sleep(0.1)
                    
                    # Smooth stop
                    write_on_bus_all_rpm(bus_config=port_config,
                                            params=BoardParams(nodo["nodo"],
                                                        nodo["rpm1"],
                                                        nodo["rpm2"],
                                                        LAST_RPM['rpm3'],
                                                        LAST_RPM['rpm4']))
                    time.sleep(0.1)
                    write_on_bus_all_rpm(bus_config=port_config,
                                            params=BoardParams(nodo["nodo"],
                                                        nodo["rpm1"],
                                                        nodo["rpm2"],
                                                        nodo["rpm3"],
                                                        LAST_RPM['rpm4']))
                    time.sleep(0.1)
                    write_on_bus_all_rpm(bus_config=port_config,
                                            params=BoardParams(nodo["nodo"],
                                                        nodo["rpm1"],
                                                        nodo["rpm2"],
                                                        nodo["rpm3"],
                                                        nodo["rpm4"]))
                LAST_RPM['rpm1'] = nodo['rpm1']
                LAST_RPM['rpm2'] = nodo['rpm2']
                LAST_RPM['rpm3'] = nodo['rpm3']
                LAST_RPM['rpm4'] = nodo['rpm4']
                
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

                from src.can_bus import available_boards_from_scan
                
                data: dict = {
                    "command": "rtaScan",
                    "nodos": available_boards_from_scan
                }
                
                node_list.extend(available_boards_from_scan)
                node_list = list(set(node_list))
                
                data = json.dumps(data).encode()
                
                conn.sendall(data)
            
            elif command == 'renombrar':
                write_on_bus_rename(bus_config=port_config,
                                    b1=BoardParams(data['nodo'], 0, 0, 0, 0),
                                    b2=BoardParams(data['nodoNombreNuevo'], 0, 0, 0, 0))
                
            elif command == 'restablecerFabrica':
                write_on_bus_factory_reset(bus_config=port_config,
                                           params=BoardParams(data['nodo'], 0, 0, 0, 0))

            elif command == 'version':
                data: dict = {
                    "version" : VERSION,
                    "board_version" : BOARD_VERSION
                }
                
                data = json.dumps(data).encode()
                
                conn.sendall(data)
                
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
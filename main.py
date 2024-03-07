from src.can_bus import reader_loop, write_on_bus_all_rpm, write_on_bus_test, write_on_bus_take_status, write_on_bus_take_rpm, buffer, port_config
from src.canbus_parser import *
from src.log import log
from threading import Thread
from time import sleep
import socket
import json
import time

""" 
Los siguientes comandos de linux sirven para levantar la interfaz can0
desde el hardware.
"""
HOST: str = '192.168.1.62'
PORT: int = 8080    
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM

sock = socket.socket(FAMILY, TYPE)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
clients: set = ()
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

class Node:
    started: bool
    id: int

def get_rmp() -> None:
    while True:
        time.sleep(1)
        try:
            for i, node in enumerate(nodes):
                if node.started:
                    write_on_bus_take_rpm(bus_config=port_config,
                                    params=BoardTest(int(node.id)))
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
            clients = clients + client
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
                    
                    sleep(0.5)
                    conn.sendall(data_meteor)
                    sleep(0.5)
                    conn.sendall(data_node_data)
                        
                except ConnectionError as e:
                    del clients[idx]
                    log(str(e), 'send_data_over_socket')
                except OSError:
                    pass
            
def send_data_over_node(client) -> None:
    while True:
        try:
            conn = client["conn"]
            data = conn.recv(1024)

            log(f'Nuevo Mensaje: {data}', 'send_data_over_node')
            
            data = json.loads(data)
            command: str = data["command"] 

            
            if command == "testing":
                for node in data["nodos"]:
                    write_on_bus_test(bus_config=port_config,
                                    params=BoardTest(node))
                
                def get_status() -> None:
                    while True:
                        time.sleep(6)
                        for node in data["nodos"]:
                            write_on_bus_take_status(bus_config=port_config,
                                            params=BoardTest(node))
                            
                simple_thread = Thread(target=get_status)
                simple_thread.start()
                
            elif command == "normal":
                write_on_bus_all_rpm(bus_config=port_config,
                                        params=BoardParams(data["nodo"],
                                                    data["rpm1"],
                                                    data["rpm2"],
                                                    data["rpm3"],
                                                    data["rpm4"]))     
                new_node = Node()
                new_node.started = True
                new_node.id = data["nodo"]
                nodes.append(new_node)
                
        except Exception as e: 
            log('Error', 'send_data_over_node')
            print("[error] send_data_over_node")
            print(e)
            break
    
if __name__ == '__main__':
    while True:
        task_wait_for_client = Thread(target=_listen_for_incomming_clients)
        task_read_node = Thread(target=reader_loop, args=(port_config,))
        task_write_into_front = Thread(target=send_data_over_socket)
        task_get_rpm = Thread(target=get_rmp)

        task_wait_for_client.start()
        task_read_node.start()
        task_write_into_front.start()
        task_get_rpm.start()
        
        task_wait_for_client.join()
        task_read_node.join()
        task_write_into_front.join()
        task_get_rpm.join()
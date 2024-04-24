from threading import Thread
from time import sleep
import socket
import random

HOST: str = '192.168.1.62'
PORT: int = 8080
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM
CONNECTED: bool = False

sock = socket.socket(FAMILY, TYPE)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen()
conn, add = sock.accept(); CONNECTED = True

def send_data_over_socket() -> None:
    global CONNECTED
    while True:
        try:
            while True:
                if not CONNECTED:
                    break
                sleep(0.5)
                string: str = f'{random.randint(9000000, 9999999999999)}\n'
                conn.sendall(string.encode())
                
        except Exception as e:
            CONNECTED = False
            print("[error] send_data_over_socket")
            print(e)
            
def send_data_over_node() -> None:
    global CONNECTED
    while True:
        try:
            while True:
                if not CONNECTED:
                    global conn, add
                    conn, add = sock.accept(); CONNECTED = True
                    break
                data = conn.recv(1024).decode()        
                if not data: break
                
                print(f'{add} > {data}')
                                                             
        except Exception as e: 
            CONNECTED = False
            print("[error] receive_data")
            print(e)
    
if __name__ == '__main__':
    task_write_into_front = Thread(target=send_data_over_socket)
    task_write_into_node = Thread(target=send_data_over_node)
    
    task_write_into_front.start()
    task_write_into_node.start()
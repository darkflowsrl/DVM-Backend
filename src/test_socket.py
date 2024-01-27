from threading import Thread
from time import sleep
import socket
import random

HOST: str = '192.168.0.6'
PORT: int = 8080
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM

def check_socket_closed(sock):
    try:
        data = sock.recv(1)
        if not data:
            return True
        else:
            return False
    except socket.error as e:
        print(f"Error de socket: {e}")
        return True


def send_data_over_socket() -> None:
    while True:
        try:
            with socket.socket(FAMILY, TYPE) as sock:
                sock.bind((HOST, PORT))
                sock.listen()
                conn, _ = sock.accept()
                with conn:
                    while True:
                        sleep(0.5)
                        string: str = f'{random.randint(9000000, 9999999999999)}\n'
                        conn.sendall(string.encode())
                
        except Exception as e:
            print("[error] send_data_over_socket")
            print(e)
            
def send_data_over_node() -> None:
    while True:
        try:
            with socket.socket(FAMILY, TYPE) as sock:
                sock.bind((HOST, PORT+1))
                sock.listen()
                conn, add = sock.accept()
                
                with conn:
                    while True:
                        data = conn.recv(1024).decode()        
                        
                        if not data: break
                        
                        print(f'{add} > {data}')
                                                             
        except Exception as e: 
            print("[error] receive_data")
            print(e)
    
if __name__ == '__main__':
    task_write_into_front = Thread(target=send_data_over_socket)
    task_write_into_node = Thread(target=send_data_over_node)
    
    task_write_into_front.start()
    task_write_into_node.start()
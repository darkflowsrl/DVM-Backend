from src.can_bus import reader_loop, write_on_bus_all_params, buffer, port_config
from threading import Thread
from time import sleep
import socket

HOST: str = '127.0.0.1'
PORT: int = 8000
FAMILY: int = socket.AF_INET
TYPE: int = socket.SOCK_STREAM

def send_data_over_socket() -> None:
    while True:
        try:
            with socket.socket(FAMILY, TYPE) as sock:
                sock.bind((HOST, PORT))
                sock.listen()
                conn, add = sock.accept()
                with conn:
                    while True:
                        conn.sendall(str(buffer.parse_dict()).encode())
                
        except Exception as e:
            print(e)
    
if __name__ == '__main__':
    task_read = Thread(target=reader_loop, args=(port_config,))
    task_write = Thread(target=send_data_over_socket)
    
    task_read.start()
    task_write.start()

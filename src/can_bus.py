from typing import List
from canbus_parser import *
import asyncio
import can
import os

port_config: CanPortConfig = CanPortConfig(interface="socketcan",
                                           channel="can0",
                                           baudrate=250000)

buffer: StateBuffer = StateBuffer()
    
def load_message(msg: can.Message) -> None:
    message_parser = Parser(msg.arbitration_id, msg.data)
    buffer: str = message_parser.parse(buffer)
    
    print(buffer)
    
def reader_loop(config: CanPortConfig) -> None:
    with can.interface.Bus(channel=config.channel,
                            interface=config.interface,
                            bitrate=config.baudrate,
                            receive_own_messages=True) as bus:
        while True:
            try:
                for message in bus:
                    load_message(message)
            except:
                pass
            
def write_on_bus_all_params(bus_config: CanPortConfig, params: BoardParams) -> None:
    id: int = 64835
    msg = can.Message(arbitration_id=id,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1],
                                        params.m1_rpm,
                                        params.m2_rpm,
                                        params.m3_rpm,
                                        params.m4_rpm, 0, 0],
                                  is_extended_id=True)
    
    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                except can.CanError:
                    print('[error] Mensaje no enviado')
                    
                    
if __name__ == '__main__':
    from threading import Thread
    
    task = Thread(target=reader_loop, args=(port_config,))
    task.start()
            
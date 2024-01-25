from typing import List
from canbus_parser import *
import asyncio
import can
import os

port_config: CanPortConfig = CanPortConfig(interface="socketcan",
                                           channel="can0",
                                           baudrate=250000)

buffer = StateBuffer()
    
def load_message(msg: can.Message) -> None:
    global buffer
    
    message_parser = Parser(msg.arbitration_id, msg.data)
    buffer = message_parser.parse(buffer)
    
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
            except Exception as e:
                print(e)
            
def write_on_bus_all_params(bus_config: CanPortConfig, params: BoardParams) -> None:
    id: int = 64835
    msg = can.Message(arbitration_id=id,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1],
                                        params.m1_rpm//50,
                                        params.m2_rpm//50,
                                        params.m3_rpm//50,
                                        params.m4_rpm//50, 0, 0],
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
    
    write_on_bus_all_params(bus_config=port_config, params=BoardParams(875, 877, 877, 877, 877))
            
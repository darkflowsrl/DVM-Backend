if __name__ == '__main__':
    from canbus_parser import *
    from log import log
else:
    from src.canbus_parser import *
    from src.log import log

import can

TEST: bool = True

port_config: CanPortConfig = CanPortConfig(interface="socketcan",
                                           channel="can0",
                                           baudrate=250000)

buffer = StateBuffer()
    
def load_message(msg: can.Message) -> None:
    global buffer

    print(f'MSG -> {msg}')
    
    message_parser = Parser(msg.arbitration_id, msg.data)
    buffer = message_parser.parse(buffer)
    
def reader_loop(config: CanPortConfig) -> None:
        while True:
            with can.interface.Bus(channel=config.channel,
                            interface=config.interface,
                            bitrate=config.baudrate,
                            receive_own_messages=True) as bus:
                try:
                    for message in bus:
                        load_message(message)
                except Exception as e:
                    print(f'Excepcion: {e}')
                    log(e, 'reader_loop')
                
def write_on_bus_all_rpm(bus_config: CanPortConfig, params: BoardParams) -> None:
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
                    print('[ok] Mensaje enviado : write_on_bus_all_rpm')
                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", 'write_on_bus_test')
                except can.CanError:
                    print('[error] Mensaje no enviado : write_on_bus_all_rpm')

def write_on_bus_test(bus_config: CanPortConfig, params: BoardTest) -> None:
    id: int = 64069
    msg = can.Message(arbitration_id=id,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1], 0, 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", write_on_bus_test)
                    print('[ok] Mensaje enviado : write_on_bus_test')
                except can.CanError:
                    print('[error] Mensaje no enviado : write_on_bus_test')
                    
if __name__ == '__main__':
    for i in range(10000):
        write_on_bus_test(port_config, BoardTest(i))
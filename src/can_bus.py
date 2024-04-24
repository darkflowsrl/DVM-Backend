
from src.canbus_parser import *
from src.log import log

import threading
import can
import time

TEST: bool = True

port_config: CanPortConfig = CanPortConfig(interface="socketcan",
                                           channel="can0",
                                           baudrate=250000)

buffer = StateBuffer()
available_boards_from_scan: list = []

class Ids:
    set_individual_rpm: int = 64835
    test_board: int = 64069
    take_test_response: int = 64070
    take_board_rpm: int = 64836
    
    config_rpm_variation: int = 10001
    config_under_currency: int = 10002
    config_over_currency: int = 10003
    config_shortage: int = 10004
    
    config_sensor: int = 10010
    config_valve: int = 10011
    
    ask_scan: int = 10020
    
    rename: int = 10030
    factory_reset: int = 10040

def clean_available_boards_from_scan() -> None:
    global available_boards_from_scan
    time.sleep(5)
    available_boards_from_scan = []

"""
La función load_message se utiliza para analizar los mensajes CAN entrantes y actualizar el búfer y las variables globales disponibles_boards_from_scan en consecuencia.

La función toma un argumento:

msg: un objeto can.Message que representa el mensaje CAN entrante.
La función primero verifica si el ID de arbitraje del mensaje está en una lista de ID de arbitraje conocidos. Si el ID de arbitraje está en la lista, el mensaje se imprime en la consola.

A continuación, la función comprueba si el ID de arbitraje del mensaje es 10021. 
Si es así, se crea un nuevo hilo para llamar a la función clean_available_boards_from_scan. La función clean_available_boards_from_scan se utiliza para borrar la lista de available_boards_from_scan después de 5 segundos.

Después de verificar el ID de arbitraje, la función crea un objeto Parser y llama al método de análisis en el objeto. 
El método de análisis toma dos argumentos:

arbitration_id: el ID de arbitraje del mensaje.
datos: Los bytes de datos del mensaje.
El método de análisis devuelve una tupla que contiene dos valores:

type_: una cadena que representa el tipo de mensaje.
analizado: los datos analizados del mensaje.
Si el valor type_ es 'new_board', la función agrega el valor analizado a la lista available_boards_from_scan. La lista available_boards_from_scan se utiliza para almacenar los ID de las placas que se han escaneado en el bus CAN.

Si el valor_tipo es 'state_buffer', la función establece la variable global del búfer en el valor analizado. La variable global del búfer se utiliza para almacenar el estado del bus CAN.
"""
def load_message(msg: can.Message) -> None:
    global buffer
    global available_boards_from_scan

    if msg.arbitration_id in [130313, 130306, 65269, 1000, 64070, 64071, 64837, 64838, 10021]: print(f'MSG -> {msg}')
    
    if msg.arbitration_id == 10021: threading.Thread(target=clean_available_boards_from_scan, daemon=True).start()
    
    message_parser = Parser(msg.arbitration_id, msg.data)
    type_, parsed = message_parser.parse(buffer)
    
    if type_ == 'new_board':
        available_boards_from_scan.append(parsed)
        available_boards_from_scan = list(set(available_boards_from_scan))
        
        print(f'[DEBUG] New board -> {parsed}')
        print(f'[DEBUG] Available boards -> {available_boards_from_scan}')
        
    elif type_ == 'state_buffer':
        buffer = parsed
    
"""
La función reader_loop se utiliza para leer continuamente mensajes del bus CAN y llamar a la función load_message
para analizar los mensajes. La función toma un argumento:

config: un objeto CanPortConfig que especifica la configuración del bus CAN que se utilizará.
La función primero crea un objeto can.interface.Bus usando la configuración especificada.
El objeto Bus se utiliza para leer mensajes del bus CAN.

Luego, la función entra en un bucle infinito. En el bucle, la función llama al bucle for para iterar
sobre los mensajes que se reciben desde el bus CAN. Para cada mensaje,
la función llama a la función load_message para analizar el mensaje.

La función load_message es responsable de analizar el mensaje CAN y actualizar el búfer
y las variables globales disponibles_boards_from_scan en consecuencia.

Si se produce una excepción al leer mensajes del bus CAN, la función imprime la excepción
en la consola y la registra en un archivo.
"""
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
                    log(f'[error] {e}', 'reader_loop')
                    print(f'[error]: {e}')
                    
                
def write_on_bus_all_rpm(bus_config: CanPortConfig,
                         params: BoardParams) -> None:    
    msg = can.Message(arbitration_id=Ids.set_individual_rpm,
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
                    # print('[ok] Mensaje enviado : write_on_bus_all_rpm')
                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", 'write_on_bus_test')
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_all_rpm')
                    print('[error] Mensaje no enviado : write_on_bus_all_rpm')

def write_on_bus_test(bus_config: CanPortConfig,
                      params: BoardTest) -> None:
    msg = can.Message(arbitration_id=Ids.test_board,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1], 0, 0, 0, 0, 0, 0],
                                  is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                    # print('[ok] Mensaje enviado : write_on_bus_test')
                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", 'write_on_bus_test')
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_test')
                    print('[error] Mensaje no enviado : write_on_bus_test')

def write_on_bus_take_status(bus_config: CanPortConfig,
                             params: BoardTest) -> None:
    msg = can.Message(arbitration_id=Ids.take_test_response,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1], 0, 0, 0, 0, 0, 0],
                                  is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)

                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", 'write_on_bus_take_status')
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_take_status')
                    print('[error] Mensaje no enviado : write_on_bus_take_status')

def write_on_bus_take_rpm(bus_config: CanPortConfig,
                          params: BoardTest) -> None:
    msg = can.Message(arbitration_id=Ids.take_board_rpm,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1], 0, 0, 0, 0, 0, 0],
                                  is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                    # print('[ok] Mensaje enviado : write_on_bus_take_rpm')
                    log(f"Mensaje Enviado: {params.board_id}:{params.board_id_bytes.hex()}", 'write_on_bus_take_rpm')
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_take_rpm')
                    print('[error] Mensaje no enviado : write_on_bus_take_rpm')

def write_on_bus_all_config(bus_config: CanPortConfig,
                            node: NodeConfiguration) -> None:    
    msg_config_rpm_variation = can.Message(arbitration_id=Ids.config_rpm_variation,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        int(node.variacion_rpm*10), 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    msg_config_under_currency = can.Message(arbitration_id=Ids.config_under_currency,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        int(node.subcorriente*10), 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    msg_config_over_currency = can.Message(arbitration_id=Ids.config_over_currency,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        int(node.sobrecorriente*10), 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    msg_config_shortage = can.Message(arbitration_id=Ids.config_shortage,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        int(node.cortocicuito*10), 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    msg_config_sensor = can.Message(arbitration_id=Ids.config_sensor,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        node.sensor, 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    msg_config_valve = can.Message(arbitration_id=Ids.config_valve,
                                  data=[node.board_id_bytes[0],
                                        node.board_id_bytes[1],
                                        node.electrovalvula, 0, 0, 0, 0, 0],
                                  is_extended_id=True)
    
    messages: list = [
                        msg_config_rpm_variation,
                        msg_config_under_currency,
                        msg_config_over_currency,
                        msg_config_shortage,
                        msg_config_sensor,
                        msg_config_valve
                    ]
    
    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    for msg in messages:
                        bus.send(msg)
                        time.sleep(0.05)
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_all_config')
                    print('[error] Mensaje no enviado : write_on_bus_all_config')      

def write_scan_boards(bus_config: CanPortConfig) -> None:
    msg = can.Message(arbitration_id=Ids.ask_scan,
                        data=[0, 0, 0, 0, 0, 0, 0, 0],
                        is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_scan_boards')
                    print('[error] Mensaje no enviado : write_scan_boards')


def write_on_bus_rename(bus_config: CanPortConfig,
                          b1: BoardTest,
                          b2: BoardTest) -> None:
    msg = can.Message(arbitration_id=Ids.rename,
                                  data=[b1.board_id_bytes[0],
                                        b1.board_id_bytes[1],
                                        b2.board_id_bytes[0],
                                        b2.board_id_bytes[1], 0, 0, 0, 0],
                                  is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_rename')
                    print('[error] Mensaje no enviado : write_on_bus_rename')

def write_on_bus_factory_reset(bus_config: CanPortConfig,
                          params: BoardTest) -> None:
    msg = can.Message(arbitration_id=Ids.factory_reset,
                                  data=[params.board_id_bytes[0],
                                        params.board_id_bytes[1], 0, 0, 0, 0, 0, 0],
                                  is_extended_id=True)

    with can.interface.Bus(channel=bus_config.channel,
                               interface=bus_config.interface,
                               bitrate=bus_config.baudrate,
                               receive_own_messages=True) as bus:
                try:
                    bus.send(msg)
                except can.CanError:
                    log('[error] Mensaje no enviado : can error', 'write_on_bus_factory_reset')
                    print('[error] Mensaje no enviado : write_on_bus_factory_reset')


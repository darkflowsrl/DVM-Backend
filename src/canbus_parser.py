"""
(Formato Python)
Guardado de los estados de los motores por cada Nodo:
[
    "nodos" : {
        "nodo" : 1030,
        "state1" : 2000,
        "state2" : 2500,
        "state3" : 3000,
        "state4" : 1500,
        "rpm1" : 2000,
        "rpm2" : 2500,
        "rpm3" : 3000,
        "rpm4" : 1500,
        "corr1" : 3.2,
        "corr2" : 3.1,
        "corr3" : 4.2,
        "corr4" : 3.4,
        "voltaje" : 12.2
    }
]

"""

from typing import List, Dict, Any, Tuple


"""
La clase NodeConfiguration se utiliza para almacenar los parámetros
de configuración para un nodo específico en el bus CAN. 
La clase tiene los siguientes atributos:

board_id: el ID del nodo.
board_id_bytes: el ID del nodo como matriz de bytes.
variacion_rpm: La variación de RPM deseada para el nodo.
subcorriente: La corriente subterránea deseada para el nodo.
sobrecorriente: La sobrecorriente deseada para el nodo.
cortocicuito: El cortocircuito deseado para el nodo.
sensor: El sensor deseado para el nodo.
electrovalvula: La electroválvula deseada para el nodo.
El método __init__() se utiliza para inicializar el objeto NodeConfiguration. 
El método toma los siguientes argumentos:

board_id: el ID del nodo.
variacion_rpm: La variación de RPM deseada para el nodo.
subcorriente: La corriente subterránea deseada para el nodo.
sobrecorriente: La sobrecorriente deseada para el nodo.
cortocicuito: El cortocircuito deseado para el nodo.
sensor: El sensor deseado para el nodo.
electrovalvula: La electroválvula deseada para el nodo.
El método parse_into_hex() se utiliza para convertir los parámetros 
de configuración en un diccionario de bytearrays. El método no toma argumentos y 
devuelve un diccionario con las siguientes claves:

variacion_rpm: La variación de RPM deseada para el nodo como bytearray.
subcorriente: La corriente subyacente deseada para el nodo como un bytearray.
sobrecorriente: La sobrecorriente deseada para el nodo como bytearray.
cortocicuito: El cortocircuito deseado para el nodo como bytearray.
El método parse_into_hex() se utiliza para convertir los parámetros de configuración 
a un formato que pueda enviarse a través del bus CAN.
"""
class NodeConfiguration:
    def __init__(self,
                 board_id: int,
                 variacion_rpm: int,
                 subcorriente: float,
                 sobrecorriente: float,
                 cortocicuito: float,
                 sensor: int,
                 electrovalvula: int) -> None:
        
        self.board_id = board_id 
        self.board_id_bytes = self.board_id.to_bytes(2, 'little')
        self.variacion_rpm = variacion_rpm
        self.subcorriente = subcorriente
        self.sobrecorriente = sobrecorriente
        self.cortocicuito = cortocicuito
        self.sensor = sensor
        self.electrovalvula = electrovalvula
    
    def parse_into_hex(self) -> Dict[str, List]:
        variacion_rpm: bytes = self.variacion_rpm.to_bytes(2, 'little')
        subcorriente: bytes = self.subcorriente.to_bytes(2, 'little')
        sobrecorriente: bytes = self.sobrecorriente.to_bytes(2, 'little')
        cortocicuito: bytes = self.cortocicuito.to_bytes(2, 'little')
        
        return {
            'variacion_rpm': variacion_rpm,
            'subcorriente': subcorriente,
            'sobrecorriente': sobrecorriente,
            'cortocicuito': cortocicuito
        }
    

class CanPortConfig:
    def __init__(self, interface: str,
                 channel: str,
                 baudrate: int) -> None:
        self.interface = interface
        self.channel = channel
        self.baudrate = baudrate


"""
La clase StateBuffer se utiliza para almacenar
el estado del bus CAN. La clase tiene los siguientes atributos:

zumbido: El nivel de humedad.
wind_dir: La dirección del viento.
wind_speed: La velocidad del viento.
temperatura: La temperatura.
pr: La presión.
node_states: una lista de diccionarios, cada uno de los cuales representa el estado de un nodo en el bus CAN.

El método put_node_states_test() se utiliza para actualizar el estado
de un nodo en la lista node_states. El método toma los siguientes argumentos:

id: el ID del nodo.
state1: el estado del primer motor en el nodo.
state2: el estado del segundo motor en el nodo.
state3: el estado del tercer motor en el nodo.
state4: el estado del cuarto motor en el nodo.
v: El voltaje del nodo.
El método put_node_states_rpm() se utiliza para actualizar las 
RPM de un nodo en la lista node_states. El método toma los siguientes argumentos:

id: el ID del nodo.
rpm1: Las RPM del primer motor en el nodo.
rpm2: Las RPM del segundo motor en el nodo.
rpm3: Las RPM del tercer motor en el nodo.
rpm4: Las RPM del cuarto motor en el nodo.
El método put_node_states_currency_voltage() se utiliza para actualizar 
la moneda y el voltaje de un nodo en la lista node_states. El método toma los siguientes argumentos:

id: el ID del nodo.
corr1: la moneda del primer motor en el nodo.
corr2: la moneda del segundo motor en el nodo.
corr3: La moneda del tercer motor en el nodo.
corr4: La moneda del cuarto motor en el nodo.
v: El voltaje del nodo.
El método parse_meteor() se utiliza para analizar los datos meteorológicos 
del objeto StateBuffer. El método devuelve un diccionario que contiene las siguientes claves:

comando: El comando que se enviará al cliente.
humedad: El nivel de humedad.
velViento: La velocidad del viento.
dirViento: La dirección del viento.
temperatura: La temperatura.
puntoDeRocio: La presión.
El método parse_node() se utiliza para analizar los datos del 
nodo del objeto StateBuffer. El método devuelve un diccionario que contiene las siguientes claves:

comando: El comando que se enviará al cliente.
nodos: una lista de diccionarios, cada uno de los cuales representa el estado de un nodo en el bus CAN.
"""
class StateBuffer:
    def __init__(self,
                 hum: int = 0,
                 wind_dir: int = 0,
                 wind_speed: int = 0,
                 temp: int = 0,
                 pr: int = 0,
                 atm_pressure: float = 0) -> None:
        self.hum: int = hum
        self.wind_dir: int = wind_dir
        self.wind_speed: int = wind_speed
        self.temp: int = temp
        self.pr: int = pr
        self.atm_pressure: float = atm_pressure
        self.interface_version: int = 0
        self.gps_state: dict = {
            "nroSatelites" : 0,
            "velocicidad" : 0,
            "latitud" : 0,
            "longitud" : 0,
            "altura" : 0
        }
        
        self.caudalimetro: dict = {
            "boards" : [
                {
                    "board_id" : -1,
                    "caudalEngine0" : 0,
                    "caudalEngine1" : 0,
                    "caudalEngine2" : 0,
                    "caudalEngine3" : 0 
                }
            ]
        }
        
        self.node_states: dict = {"command" : "estadoGeneralNodos",
                                  "nodos" : []}
        
    def put_node_states_test(self,
                        id: int,
                        state1: int,
                        state2: int,
                        state3: int,
                        state4: int,
                        v: float) -> None:
        
        for node in self.node_states["nodos"]:
            if node["nodo"] == id:
                node["state1"] = state1
                node["state2"] = state2
                node["state3"] = state3
                node["state4"] = state4
                node["voltaje"] = v
                
                return
        
        self.node_states["nodos"].append(
            {
                "nodo" : id,
                "state1" : state1,
                "state2" : state2,
                "state3" : state3,
                "state4" : state4,
                "voltaje" : v
            }
        )
        
        return
        
    def put_node_states_rpm(self,
                        id: int,
                        rpm1: int,
                        rpm2: int,
                        rpm3: int,
                        rpm4: int) -> None:
        
        for node in self.node_states["nodos"]:
            if node["nodo"] == id:
                node["rpm1"] = rpm1
                node["rpm2"] = rpm2
                node["rpm3"] = rpm3
                node["rpm4"] = rpm4

                return
        
        self.node_states["nodos"].append(
            {
                "nodo" : id,
                "rpm1" : rpm1,
                "rpm2" : rpm2,
                "rpm3" : rpm3,
                "rpm4" : rpm4,
            })
        
        return
    
    def put_node_states_currency_voltage(self,
                        id: int,
                        corr1: int,
                        corr2: int,
                        corr3: int,
                        corr4: int,
                        v: float) -> None:
        
        for node in self.node_states["nodos"]:
            if node["nodo"] == id:
                node["corr1"] = corr1
                node["corr2"] = corr2
                node["corr3"] = corr3
                node["corr4"] = corr4
                node["voltaje"] = v
                
                return
        
        self.node_states["nodos"].append(
            {
                "nodo" : id,
                "corr1" : corr1,
                "corr2" : corr2,
                "corr3" : corr3,
                "corr4" : corr4,
                "voltaje" : v
            })
        
        return
    
    def parse_meteor(self) -> dict:
        return {
            "command" : "datosMeteorologicos",
            "humedad" : self.hum,
            "velViento" : self.wind_speed,
            "dirViento" : self.wind_dir,
            "temperatura" : self.temp,
            "puntoDeRocio" : self.pr,
            "presionAtmosferica" : round(self.atm_pressure, 1),
            "version" : self.interface_version,
            "gpsInfo" : self.gps_state,
            "caudalInfo" : self.caudalimetro
        }
        
    def parse_node(self) -> dict:
        return self.node_states
    
    def update_caudal(self, board_id: int,
                      engine_number: int,
                      caudal: float) -> None:
        for board in self.caudalimetro["boards"]:
            if board["board_id"] == board_id:
                board["caudalEngine" + str(engine_number)] = caudal
                return
        
        self.caudalimetro["boards"].append(
            {
                "board_id" : board_id,
                "caudalEngine0" : 0,
                "caudalEngine1" : 0,
                "caudalEngine2" : 0,
                "caudalEngine3" : 0
            }
        )
        
        return
    
    def get_caudal(self, board_id: int) -> dict:
        for board in self.caudalimetro["boards"]:
            if board["board_id"] == board_id:
                return board
        return {}
    
"""
La clase Parser se utiliza para analizar mensajes
CAN entrantes y actualizar la variable global
mod_buffer en consecuencia.

La clase toma dos argumentos:

id: el ID de arbitraje del mensaje.
datos: Los bytes de datos del mensaje.
La clase primero verifica el ID de arbitraje del mensaje
para determinar qué tipo de mensaje es. Si el ID de arbitraje
es uno de los siguientes, la clase actualiza el campo correspondiente en el objeto mod_buffer:

130313: Humedad
130306: Velocidad y dirección del viento
65269: Temperatura
1000: presión
64071: Estados de nodo (prueba)
64837: Estados de nodo (RPM)
64838: Estados de los nodos (moneda y voltaje)
Si el ID de arbitraje es 10021, la clase devuelve una tupla
que contiene la cadena 'new_board' y el ID del nuevo tablero.

De lo contrario, la clase devuelve una tupla que contiene
la cadena 'state_buffer' y el objeto mod_buffer actualizado.
"""
class Parser:
    def __init__(self, id: int, data: bytearray) -> None:
        self.id = id
        self.data = data
        self.data_int = int.from_bytes(self.data, byteorder='little')
        
    def parse(self, mod_buffer: StateBuffer) -> Tuple[str, Any]:
        if self.id == 130313:
            humidity: float = round(self.data_int * 0.004, 2)
            mod_buffer.hum = humidity
        
        elif self.id == 130306:
            speed: float = round( int.from_bytes(self.data[0:2], byteorder='little') * 0.01, 2)
            dir: float = round((int.from_bytes(self.data[2:], byteorder='little') * 0.0001) * 180 / 3.14159 , 2)
            
            mod_buffer.wind_speed = speed
            mod_buffer.wind_dir = dir
            
        elif self.id == 65269:
            temp: float = round(self.data_int * 0.01 - 273.15, 2)
            mod_buffer.temp = temp            
            
        elif self.id == 1000:
            pr: float = round(self.data_int * 0.01 - 273.15, 2)
            mod_buffer.pr = pr
        
        elif self.id == 64071:
            id_board: int = int.from_bytes(self.data[0:2], byteorder='little')
            state1: int = self.data[2]
            state2: int = self.data[3]
            state3: int = self.data[4]
            state4: int = self.data[5]
            
            voltaje: int = self.data[6] * 0.1
            
            mod_buffer.put_node_states_test(id_board,
                                            state1,
                                            state2,
                                            state3,
                                            state4,
                                            voltaje)
        
        elif self.id == 64837:
            id_board: int = int.from_bytes(self.data[0:2], byteorder='little')
            rpm1: int = self.data[2] * 50
            rpm2: int = self.data[3] * 50
            rpm3: int = self.data[4] * 50
            rpm4: int = self.data[5] * 50
            
            mod_buffer.put_node_states_rpm(id_board,
                                            rpm1,
                                            rpm2,
                                            rpm3,
                                            rpm4)
        
        elif self.id == 64838:
            id_board: int = int.from_bytes(self.data[0:2], byteorder='little')
            corr1: int = self.data[2]
            corr2: int = self.data[3]
            corr3: int = self.data[4]
            corr4: int = self.data[5]
            
            voltaje: int = self.data[6] * 0.1
            
            mod_buffer.put_node_states_currency_voltage(id_board,
                                            corr1,
                                            corr2,
                                            corr3,
                                            corr4,
                                            voltaje)
            
        elif self.id == 130314:
            mod_buffer.atm_pressure = self.data_int * 0.1

        elif self.id == 10021:
            return 'new_board', int.from_bytes(self.data[0:2], byteorder='little')
        
        elif self.id == 10051:
            mod_buffer.interface_version = int(self.data[0])
            
        elif self.id == 129026:
            mod_buffer.gps_state["velocicidad"] = self.data_int * 0.01

        elif self.id == 129029:
            mod_buffer.gps_state["latitud"] = self.data_int * 1e-6
            
        elif self.id == 129030:
            mod_buffer.gps_state["longitud"] = self.data_int * 1e-6
            
        elif self.id == 129031:
            mod_buffer.gps_state["altura"] = self.data_int * 1e-6
            
        elif self.id == 129031:
            mod_buffer.gps_state["nroSatelites"] = self.data_int
            
        elif self.id == 50432:
            board_id: int = int.from_bytes(self.data[0:2], byteorder='little')
            engine_number: int = self.data[2]
            caudal: float = int.from_bytes(self.data[3:5], byteorder='little') * 0.1

            mod_buffer.update_caudal(board_id=board_id,
                                     engine_number=engine_number,
                                     caudal=caudal)
            
        return "state_buffer", mod_buffer

"""
La clase BoardParams se utiliza para almacenar los parámetros de una placa
específica en el bus CAN. La clase tiene los siguientes atributos:

board_id: El ID del tablero.
board_id_bytes: el ID de la placa como bytearray.
m1_rpm: Las RPM deseadas para el motor 1 en el tablero.
m2_rpm: Las RPM deseadas para el motor 2 en el tablero.
m3_rpm: Las RPM deseadas para el motor 3 en el tablero.
m4_rpm: Las RPM deseadas para el motor 4 en el tablero.

El método __init__() se utiliza para inicializar el objeto BoardParams. 
El método toma los siguientes argumentos:

board_id: El ID del tablero.
m1_rpm: Las RPM deseadas para el motor 1 en el tablero.
m2_rpm: Las RPM deseadas para el motor 2 en el tablero.
m3_rpm: Las RPM deseadas para el motor 3 en el tablero.
m4_rpm: Las RPM deseadas para el motor 4 en el tablero.
El atributo board_id_bytes se crea convirtiendo el atributo board_id en un bytearray 
utilizando el método to_bytes(). El método to_bytes() toma los siguientes argumentos:

longitud: La longitud del bytearray.
byteorder: el orden de bytes de la matriz de bytes.
El argumento del orden de bytes puede ser "pequeño" o "grande". 
En este caso, el argumento de orden de bytes se establece en
"pequeño" porque el bus CAN utiliza ordenación de bytes little-endian.
"""
class BoardParams:
    def __init__(self,
                 board_id: int,
                 m1_rpm: int,
                 m2_rpm: int,
                 m3_rpm: int,
                 m4_rpm: int) -> None:
        
        self.board_id = board_id
        self.board_id_bytes = self.board_id.to_bytes(2, 'little')
        self.m1_rpm = m1_rpm
        self.m2_rpm = m2_rpm
        self.m3_rpm = m3_rpm
        self.m4_rpm = m4_rpm

class BoardTest:
    def __init__(self,
                 board_id: int) -> None:
        
        self.board_id = board_id
        self.board_id_bytes = self.board_id.to_bytes(2, 'little')
    
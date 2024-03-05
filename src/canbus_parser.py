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
class CanPortConfig:
    def __init__(self, interface: str,
                 channel: str,
                 baudrate: int) -> None:
        self.interface = interface
        self.channel = channel
        self.baudrate = baudrate

class StateBuffer:
    def __init__(self,
                 hum: int = 0,
                 wind_dir: int = 0,
                 wind_speed: int = 0,
                 temp: int = 0,
                 pr: int = 0) -> None:
        self.hum: int = hum
        self.wind_dir: int = wind_dir
        self.wind_speed: int = wind_speed
        self.temp: int = temp
        self.pr: int = pr
        self.node_states: dict = {"command" : "estadoGeneralNodos",
                                  "nodos" : []}
        
    def put_node_states_test(self,
                        id: int,
                        state1: int,
                        state2: int,
                        state3: int,
                        state4: int,
                        v: float) -> None:
        
        for k, node in enumerate(self.node_states["nodos"]):
            if node["nodo"] == id:
                self.node_states["nodos"][k]["state1"] = state1
                self.node_states["nodos"][k]["state2"] = state2
                self.node_states["nodos"][k]["state3"] = state3
                self.node_states["nodos"][k]["state4"] = state4
                self.node_states["nodos"][k]["voltaje"] = v
                
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
        
        for k, node in enumerate(self.node_states["nodos"]):
            if node["nodo"] == id:
                self.node_states["nodos"][k]["rpm1"] = rpm1
                self.node_states["nodos"][k]["rpm2"] = rpm2
                self.node_states["nodos"][k]["rpm3"] = rpm3
                self.node_states["nodos"][k]["rpm4"] = rpm4

                return
        
        self.node_states["nodos"].append({
            {
                "nodo" : id,
                "rpm1" : rpm1,
                "rpm2" : rpm2,
                "rpm3" : rpm3,
                "rpm4" : rpm4,
            }
        })
        
        return
    
    def put_node_states_currency_voltage(self,
                        id: int,
                        corr1: int,
                        corr2: int,
                        corr3: int,
                        corr4: int,
                        v: float) -> None:
        
        for k, node in enumerate(self.node_states["nodos"]):
            if node["nodo"] == id:
                self.node_states["nodos"][k]["corr1"] = corr1
                self.node_states["nodos"][k]["corr2"] = corr2
                self.node_states["nodos"][k]["corr3"] = corr3
                self.node_states["nodos"][k]["corr4"] = corr4
                self.node_states["nodos"][k]["voltaje"] = v
                
                return
        
        self.node_states["nodos"].append({
            {
                "nodo" : id,
                "corr1" : corr1,
                "corr2" : corr2,
                "corr3" : corr3,
                "corr4" : corr4,
                "voltaje" : v
            }
        })
        
        return
    
    def parse_meteor(self) -> dict:
        return {
            "command" : "datosMeteorologicos",
            "humedad" : self.hum,
            "velViento" : self.wind_speed,
            "dirViento" : self.wind_dir,
            "temperatura" : self.temp,
            "puntoDeRocio" : self.pr
        }
        
    def parse_node(self) -> dict:
        return self.node_states

class Parser:
    def __init__(self, id: int, data: bytearray) -> None:
        self.id = id
        self.data = data
        self.data_int = int.from_bytes(self.data, byteorder='little')
        
    def parse(self, mod_buffer: StateBuffer) -> StateBuffer:
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
        
        return mod_buffer
    
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
    
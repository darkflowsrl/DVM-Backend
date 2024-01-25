from copy import deepcopy

class CanPortConfig:
    def __init__(self, interface: str,
                 channel: str,
                 baudrate: int) -> None:
        self.interface = interface
        self.channel = channel
        self.baudrate = baudrate

class StateBuffer:
    def __init__(self,
                 hum: int = None,
                 wind_dir: int = None,
                 wind_speed: int = None,
                 temp: int = None,
                 pr: int = None) -> None:
        self.hum = hum
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.temp = temp
        self.pr = pr
        self.engine_states = {}
        
    def parse_dict(self) -> dict:
        return {
            "humedad" : self.hum,
            "velViento" : self.wind_speed,
            "dirViento" : self.wind_dir,
            "temperatura" : self.temp,
            "puntoDeRocio" : self.pr
        }
    
    def __str__(self) -> str:
        return str(self.parse_dict())

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
        
        else:
            ...
        
        return deepcopy(mod_buffer)
    
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
    
if __name__ == '__main__':
    m = StateBuffer()
    
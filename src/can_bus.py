from typing import List
import asyncio
import can
import argparse

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("-m", "--mode", type=str)
cli_parser.add_argument("-i", "--interface", type=str)
cli_parser.add_argument("-c", "--channel", type=str)
cli_parser.add_argument("-b", "--bitrate", type=int)

args = cli_parser.parse_args()

buffer_len: int = 1000
buffer: list = []

class Message:
    def __init__(self,
                 hum: int,
                 wind_dir: int,
                 wind_speed: int,
                 temp: int,
                 dp: int) -> None:
        self.hum = hum
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.temp = temp
        self.dp = dp
        
    def parse_dict(self) -> dict:
        return {
            "humedad" : self.hum,
            "velViento" : self.wind_speed,
            "dirViento" : self.wind_dir,
            "temperatura" : self.temp,
            "puntoDeRocio" : self.dp
        }

class Parser:
    def __init__(self, id: int, data: bytearray) -> None:
        self.id = id
        self.data = data
        self.data_int = int.from_bytes(self.data, byteorder='little')
        
    def parse(self) -> str:
        if self.id == 130313:
            return f"Humedad: {str(self.data_int * 0.004)} %" 
        if self.id == 130306:
            speed: float = int.from_bytes(self.data[0:2], byteorder='little') * 0.01
            dir: float = int.from_bytes(self.data[2:], byteorder='little') * 0.0001
            
            return f"Velocidad: {speed}m/s\nDireccion: {dir} rad"
        if self.id == 65269:
            temp: float = self.data_int * 0.01 - 273.15
            
            return f"Temperatura: {temp} °C"
        if self.id == 1000:
            pr: float = self.data_int * 0.01 - 273.15
            return f"Punto de rocio: {pr} °C"
        """
        if self.id == 129029:
            return ""
        if self.id == 129030:
            return ""
        if self.id == 129031:
            return ""
        if self.id == 129032:
            return ""
        """
        
        return None
    
    
def load_message(msg: can.Message) -> None:
    if len(buffer) >= buffer_len:
        buffer.pop()
        buffer.append(msg)
        message_parser = Parser(msg.arbitration_id, msg.data)
        parsed_msg: str = message_parser.parse()
        if parsed_msg != None: print(f"> {parsed_msg}")
    else:
        buffer.append(msg)
        message_parser = Parser(msg.arbitration_id, msg.data)
        
        parsed_msg: str = message_parser.parse()
        if parsed_msg != None: print(f"> {parsed_msg}")

async def main() -> None:
    if args.mode == "read":
        with can.interface.Bus(channel=args.channel,
                               interface=args.interface,
                               bitrate=args.bitrate,
                               receive_own_messages=True) as bus:
            reader = can.AsyncBufferedReader()
            logger = can.Logger("logfile.asc")

            listeners: List[can.notifier.MessageRecipient] = [
                    load_message, 
                    reader, 
                    logger, 
            ]
            
            loop = asyncio.get_running_loop()
            notifier = can.Notifier(bus, listeners, loop=loop)    

            for _ in range(10):
                msg = await reader.get_message()
                await asyncio.sleep(0.5)
                msg.arbitration_id += 1
                bus.send(msg)
                
            await reader.get_message()
            print("[end]")
            notifier.stop()


        #read_thread = Thread()
        #read_thread.run()
        
    elif args.mode == "write":
        while True:
            send: str = input("> ") 

if __name__ == '__main__':
    asyncio.run(main())
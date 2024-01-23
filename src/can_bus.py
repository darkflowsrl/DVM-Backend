from threading import Thread
import can
import argparse

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("-m", "--mode", type=str)
cli_parser.add_argument("-i", "--interface", type=str)
cli_parser.add_argument("-c", "--channel", type=str)
cli_parser.add_argument("-b", "--bitrate", type=int)

args = cli_parser.parse_args()

class CanController:
    def __init__(self, bus_interface: str, channel: str, bitrate: int) -> None:
        self.bus_interface = bus_interface
        self.channel = channel
        self.bitrate = bitrate
        self.bus = can.interface.Bus(interface=self.bus_interface,
                           channel=self.channel,
                           bitrate  = self.bitrate,
                            receive_own_messages=True)  
        self.buffer: list = []
        self.buffer_len: int = 1000
        
    def start_reader(self) -> str:
        if len(self.buffer) >= self.buffer_len:
            for msg in self.bus:
                self.buffer.pop()
                self.buffer.append(msg)
                print(f"{msg.arbitration_id}: {msg.data}")
        else:
            for msg in self.bus:
                self.buffer.append(msg)
                print(f"{msg.arbitration_id}: {msg.data}")


if __name__ == '__main__':
    if args.mode == "read":
        controller = CanController(bus_interface=args.interface,
                                channel=args.channel,
                                bitrate=args.bitrate)
        
        while True:
            controller.start_reader()
            controller.bus.shutdown()
            
        
        #read_thread = Thread()
        #read_thread.run()
        
    elif args.mode == "write":
        while True:
            send: str = input("> ") 
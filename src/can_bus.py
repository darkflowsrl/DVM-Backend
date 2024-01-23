from threading import Thread
import can
import argparse

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("interface")
cli_parser.add_argument("channel")
cli_parser.add_argument("bitrate")

args = cli_parser.parse_args()

class CanController:
    def __init__(self, interface: str, channel: str, bitrate: int) -> None:
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.bus = can.Bus(interface=self.interface,
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
    controller = CanController(interface='socketcan',
                               channel='can0',
                               bitrate=250000)
    
    read_thread = Thread(controller.start_reader)
    read_thread.run()
import can
from threading import Thread

class CanController:
    def __init__(self, interface: str, channel: str) -> None:
        self.interface = interface
        self.channel = channel
        self.bus = can.Bus(interface=self.interface,
                           channel=self.channel,
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
    controller = CanController(interface=None,
                               channel='can0')
    
    read_thread = Thread(controller.start_reader)
    read_thread.run()
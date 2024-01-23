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
buffer: int = 1000

def load_message(msg: can.Message) -> None:
    if len(buffer) >= buffer_len:
            for msg in bus:
                buffer.pop()
                buffer.append(msg)
                print(f"{msg.arbitration_id}: {msg.data}")
    else:
        for msg in bus:
            buffer.append(msg)
            print(f"{msg.arbitration_id}: {msg.data}")

if __name__ == '__main__':
    if args.mode == "read":
        with can.interface.Bus(channel=args.channel,
                               interface=args.interface,
                               bitrate=args.bitrate) as bus:
            
            reader = can.AsyncBufferedReader()
            logger = can.Logger("logfile.asc")

            listeners: List[can.notifier.MessageRecipient] = [
            load_message, 
            reader, 
            logger, 
            ]
            
            loop = asyncio.get_running_loop()
            notifier = can.Notifier(bus, listeners, loop=loop)    
        

        #read_thread = Thread()
        #read_thread.run()
        
    elif args.mode == "write":
        while True:
            send: str = input("> ") 
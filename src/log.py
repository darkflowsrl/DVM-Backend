import os 
import datetime

LOG_PATH: str = os.path.join(os.getcwd(), 'log.txt')

def _check_log_file(MAX: int = 10) -> None:
    if not os.path.isfile(LOG_PATH):
        # Create file if not exist
        open(LOG_PATH, 'x')

        return 
    
    # Rewrite file if is over a specified size
    size: int = os.path.getsize(LOG_PATH)
    if size//1000000 >= MAX: open(LOG_PATH, "w").close()


def log(message: str, instance: any = 'Unknow Instance') -> None:
    try:
        _check_log_file()
        
        now: str = str(datetime.datetime.now())
        now = now.split('.')[0]

        message = f'[{now}] {instance} -> {message}\n'
        
        with open(LOG_PATH, 'a') as f:
            f.write(message)
            f.close()

    except Exception as e:
        print(e)
        raise e
    
if __name__ == '__main__':
    for i in range(100):
        log(i, __name__)
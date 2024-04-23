import os
import datetime
import csv

LOG_DIR: str = os.path.join(os.getcwd(), 'logs')

def _check_log_file() -> None:
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)

def get_log_path() -> str:
    today_date = datetime.date.today()
    log_filename = f"log_{today_date}.csv"
    return os.path.join(LOG_DIR, log_filename)

def log(message: str, instance: any = 'Unknow Instance') -> None:
    try:
        _check_log_file()
        
        log_path = get_log_path()
        
        now: str = str(datetime.datetime.now())
        now = now.split('.')[0]

        if not os.path.isfile(log_path):
            with open(log_path, 'w', newline='') as csvfile:
                fieldnames = ['Timestamp', 'Instance', 'Message']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        
        with open(log_path, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Instance', 'Message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writerow({'Timestamp': now, 'Instance': instance, 'Message': message})

    except Exception as e:
        print(e)
        raise e

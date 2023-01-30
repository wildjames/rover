import gpiozero
import os
import threading
from datetime import datetime
import psutil


LOGFILE = '/home/rover/rover/rover_environment.log'
LOG_INTERVAL = 60
LOG_PURGE_INTERVAL = 60 * 60 * 24 * 7  # 1 week

LOG_THREAD = None

def log_environment():
    """Periodically gather data and log it to a file.

    The file should be of the format:
        <variablename>,<timestamp>,<value>
    """
    global LOG_THREAD

    if not os.path.exists(LOGFILE):
        with open(LOGFILE, 'w') as f:
            f.write('variable,timestamp,value\n')
    
    with open(LOGFILE, 'a') as f:
        # Gather data
        f.write('temperature,{},{}\n'.format(datetime.isoformat(), gpiozero.CPUTemperature().temperature))
        f.write('cpu_usage,{},{}\n'.format(datetime.isoformat(), psutil.cpu_percent()))
        f.write('memory_usage,{},{}\n'.format(datetime.isoformat(), psutil.virtual_memory().percent))

    # Schedule the next run
    if LOG_THREAD is not None:
        LOG_THREAD.cancel()

    LOG_THREAD = threading.Timer(5, log_environment)
    LOG_THREAD.start()


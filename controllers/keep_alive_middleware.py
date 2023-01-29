from functools import wraps
import logging
import time


last_message = time.time()


def keep_alive(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global last_message
        
        current_time = time.time()
        delta_time = current_time - last_message
        
        print("It has been {:.3f} seconds since the last message".format(delta_time))
        
        last_message = current_time

        return f(*args, **kwargs)

    return decorated

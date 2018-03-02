import sys
from datetime import datetime

import threading
import traceback

UPDATE_GUI_INTERVAL = 0.5

__thread_lock = threading.Lock()
__log_file = open('Logger.log', 'at', 0)

def LOG_CURRENT_EXCEPTION():
    with __thread_lock:
        frame = sys._getframe(1)
        filename = frame.f_code.co_filename
        linenumber = frame.f_lineno
        print >> __log_file, datetime.now().strftime('%H:%M:%S.%f %s:%d' % (filename, linenumber))
        traceback.print_exc(file=__log_file)


def LOG_DEBUG(*args):
    with __thread_lock:
        print >> __log_file, datetime.now().strftime('%H:%M:%S.%f'), ' '.join(map(str, args))


def LOG_ERROR(*args):
    with __thread_lock:
        print >> __log_file, datetime.now().strftime('%H:%M:%S.%f'), ' '.join(map(str, args))




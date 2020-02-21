
import datetime

def now_object():
    return datetime.datetime.now()

def now():
    return int(datetime.datetime.now().timestamp())

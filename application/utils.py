import string
import random
import os

from datetime import datetime


def get_current_time():
    return datetime.utcnow()


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

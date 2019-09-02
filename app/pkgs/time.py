import time
import datetime


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r  %2.4f ms' %
              (method.__name__, (te - ts) * 1000))
        return result

    return timed


def time_to_int(t: datetime.datetime):
    return (t - datetime.datetime(1970, 1, 1)).total_seconds()

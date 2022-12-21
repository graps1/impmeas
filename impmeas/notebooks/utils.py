import time

def time_op(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        val = func(*args, **kwargs)
        dt_s = (time.time() - start)
        print(f"[{dt_s*1000:010.4f} ms / {dt_s:04.4f} s / {dt_s/60:02.4f} min] {func.__name__}")
        return val
    return wrapper

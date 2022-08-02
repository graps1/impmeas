from .buddy import Buddy, BuddyFunc
import time
from functools import lru_cache 

def time_op(func):
    def wrapper(*args, **kwargs):
        dt = time.time()
        val = func(*args, **kwargs)
        print(f"[{(time.time() - dt)*1000:010.4f} ms] {func.__name__}{args}")
        return val
    return wrapper

@time_op
def u_influence(f : BuddyFunc, x : str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    f1 = f.restrict(f, x)
    f0 = f.restrict(f, f"~{x}")
    if monotone_in_x:
        return (f1.count - f0.count)
    else:
        return (f1 ^ f0).count

'''
@time_op
def u_blame(model, x, f, rho=lambda x: 1/(x+1)):
    @lru_cache(maxsize=10000)
    def g(x,f,c,k,Y):
        if k == 0:
            low = model.restrict(f, x, False)
            high = model.restrict(f, x, True)
            f_x = model.ite(model.var(x), low, high) # flips x
            equiv_c = model.apply("<->", f, c)
            return model.apply("&", model.apply("^", f, f_x), equiv_c) # (f xor f^x) & (f <-> c)
        else:
            result = False 
            for y in Y:
                Y_minus_y = list(Y)
                Y_minus_y.remove(y)
                Y_minus_y = tuple(Y_minus_y)
                f0, f1 = model.restrict(f, y, False), model.restrict(f, y, True)
                g0 = g(x,f0,c,k-1,Y_minus_y) # cannot be written as g0, g1 = ...
                g1 = g(x,f1,c,k-1,Y_minus_y) # don't know why, but leads to crash
                result = model.apply("|", result, model.ite(model.var(y), g0, g1))
            return result

    @lru_cache(maxsize=1000)
    def ell(x,f,c,k):
        result = True
        Y = tuple(set(model.name_dict) - { x })
        for i in range(k): 
            result = model.apply("&", result, model.apply("~", g(x, f, c, i, Y)))
        return model.apply("&", result, g(x, f, c, k, Y))

    result = 0
    for k in range(len(model.var_dict)): 
        if rho(k) > 0:
            term = model.ite(f, ell(x,f,1,k), ell(x,f,0,k))
            count = model.lncount(term)
            count = 2**count if count!=-1 else 0
            result += rho(k)*count
    return result

@time_op
def omega(model, f):
    @lru_cache(maxsize=10000)
    def rec(model, f):
        if f in [0,1]:
            return f
        else:
            low, high = model.low(f), model.high(f)
            low_tf = rec(model, model.apply("&", low, high))
            high_tf = model.apply("|", rec(model, low), rec(model, high))
            x = model.top_level_var(f)
            return model.ite(x, high_tf, low_tf)
    return rec(model, f)
'''
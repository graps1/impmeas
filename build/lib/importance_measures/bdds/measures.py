from .buddy import BuddyFunc
import time
from functools import lru_cache 

def u_influence(f : BuddyFunc, x : str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    x = f.model.parse(x)
    f1 = f.restrict(x)
    f0 = f.restrict(~x)
    if monotone_in_x:
        return (f1.count - f0.count)
    else:
        return (f1 ^ f0).count

def u_blame(f : BuddyFunc, x : str, rho=lambda x: 1/(x+1)):
    model = f.model
    xf = model.parse(x)

    @lru_cache(maxsize=10000)
    def g(f,c,k,Y):
        if k == 0:
            low = f.restrict(~xf)
            high = f.restrict(xf)
            f_x = xf.ite(low, high) # flips x
            return (f^f_x) & (f==c)
        else:
            result = model.false 
            for y in Y:
                Y_minus_y = list(Y)
                Y_minus_y.remove(y)
                Y_minus_y = tuple(Y_minus_y)
                yf = model.parse(y)
                f0 = f.restrict(~yf)
                f1 = f.restrict(yf)
                g0 = g(f0,c,k-1,Y_minus_y) # cannot be written as g0, g1 = ...
                g1 = g(f1,c,k-1,Y_minus_y) # don't know why, but leads to crash
                result |= yf.ite(g0, g1)
            return result

    @lru_cache(maxsize=10000)
    def ell(f,c,k):
        result = model.true
        Y = tuple(set(model.vars) - { x })
        for i in range(k): result &= ~g(f, c, i, Y)
        return result & g(f, c, k, Y) 

    result = 0
    for k in range(model.varcount): 
        if rho(k) > 0:
            term = f.ite(ell(f, model.true, k), ell(f, model.false, k))
            result += rho(k)*term.count
    return result

def omega(f):
    @lru_cache(maxsize=10000)
    def rec(f):
        if f.var is None:
            return f
        else:
            low, high = f.low, f.high
            low_tf = rec(low & high)
            high_tf = rec(low) | rec(high)
            return f.var.ite(high_tf, low_tf)
    return rec(f)
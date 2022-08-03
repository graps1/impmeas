from .buddy import BuddyNode
from functools import lru_cache 

def u_influence(f : BuddyNode, x : str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    xf = f.model.node(x)
    f1, f0 = f.restrict(xf), f.restrict(~xf)
    if monotone_in_x:
        return (f1.count - f0.count)
    else:
        return (f1 ^ f0).count

def u_blame(f : BuddyNode, x : str, rho=lambda x: 1/(x+1)):
    model = f.model
    xf = model.node(x)

    @lru_cache(maxsize=10000)
    def g(f,c,k,Y):
        if k == 0:
            f0, f1 = f.restrict(~xf), f.restrict(xf)
            f_x = xf.ite(f0, f1) # flips x
            return (f^f_x) - (f^c)
        else:
            result = model.false 
            for y in Y:
                Y_minus_y = list(Y)
                Y_minus_y.remove(y)
                Y_minus_y = tuple(Y_minus_y)
                yf = model.node(y)
                f0, f1 = f.restrict(~yf), f.restrict(yf)
                g0 = g(f0,c,k-1,Y_minus_y) # cannot be written as g0, g1 = ...
                g1 = g(f1,c,k-1,Y_minus_y) # don't know why, but leads to crash
                result |= yf.ite(g0, g1)
            return result

    @lru_cache(maxsize=10000)
    def ell(f,c,k):
        result = model.true
        Y = tuple(set(model._vars) - { x })
        for i in range(k): result &= ~g(f, c, i, Y)
        return result & g(f, c, k, Y) 

    result = 0
    for k in range(model.varcount): 
        if rho(k) > 0:
            term = f.ite(ell(f, model.true, k), ell(f, model.false, k))
            result += rho(k)*term.count
    return result

@lru_cache(maxsize=10000)
def omega(f : BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return f.model.node(f.var).ite(high_tf, low_tf)
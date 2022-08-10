from collections import defaultdict
from .buddy import BuddyNode
from functools import lru_cache, cache

def influence(f : BuddyNode, x : str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    xf = f.model.node(x)
    f1, f0 = f.restrict(xf), f.restrict(~xf)
    if monotone_in_x:
        return (f1.satcount - f0.satcount) / 2**f.model.varcount
    else:
        return (f1 ^ f0).satcount / 2**f.model.varcount

def blame(f : BuddyNode, x : str, rho=lambda x: 1/(x+1), cutoff = 1e-4, debug=False):
    if debug: print(f"=== COMPUTING BLAME for {x} in BDD with size {f.nodecount} ===")
    model = f.model

    @cache
    def g(f,c,k):
        if x not in f.depends_on:
            return model.false
        elif k == 0:
            return (f ^ f.flip(x)) - (f ^ c)
        else:
            g_last = g(f,c,k-1)
            result = g_last
            for y in f.depends_on - { x }:
                result |= g_last.flip(y)
            return result

    result = 0
    last_g = model.false
    ub_max_increase = 1 
    stopped_earlier = False
    for k in range(model.varcount):
        # early stopping criteria
        if rho(k) == 0:
            if debug: print("stopped because rho({k}) = 0")
            stopped_earlier = True
            break
        if ub_max_increase <= cutoff:
            if debug: 
                print("stopped earlier because cannot improve above cutoff.")
                print(f"current value: {result:.4f}, can be increased by {ub_max_increase:.4f} <= {cutoff:.4f}.")
            stopped_earlier = True
            break
        new_g = f.ite(g(f, model.true, k), g(f, model.false, k) )
        if last_g == new_g: # is this valid?
            break
        ell = new_g & ~last_g
        last_g = new_g
        d_result = rho(k)*ell.satcount / 2**model.varcount
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - new_g.satcount / 2**model.varcount)
        if debug: 
            print(f"k {k}", end=" ")
            print(f"size g {new_g.nodecount}", end=" ")
            print(f"size ell {ell.nodecount}", end=" ") 
            print(f"d result {d_result:.4f}", end=" ")
            print(f"max increase possible {ub_max_increase:.4f}")
    if not stopped_earlier: ub_max_increase = 0
    if debug: print(f"=== DONE ===")
    return result, result + ub_max_increase

@cache
def omega(f : BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return f.model.node(f.var).ite(high_tf, low_tf)
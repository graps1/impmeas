from formulas import BuddyNode
from functools import cache

def influence(f: BuddyNode, x: str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    f0, f1 =  f.branch(x)
    if monotone_in_x:
        return (f1.satcount() - f0.satcount()) / 2**f.ctx.varcount
    else:
        return (f1 ^ f0).satcount() / 2**f.ctx.varcount

def blame(f: BuddyNode, x: str, rho=lambda x: 1/(x+1), cutoff = 1e-4, debug=False):
    if debug: print(f"=== COMPUTING BLAME for {x} in BDD with size {f.nodecount} ===")

    @cache
    def g(f,c,k):
        if x not in f.vars:
            return f.ctx.false
        elif k == 0:
            return (f ^ f.flip(x)) & (f.biimp(c))
        else:
            g_last = g(f,c,k-1)
            result = g_last
            for y in f.vars - { x }:
                result |= g_last.flip(y)
            return result

    result = 0
    last_ell_sc = 0
    ub_max_increase = 1 
    last_g_high, last_g_low = f.ctx.false, f.ctx.false
    stopping_reason = "finished iteration."
    for k in range(f.ctx.varcount):
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = f"stopped because rho({k}) = 0"
            break

        g_high, g_low = g(f, f.ctx.true, k), g(f, f.ctx.false, k)
        if last_g_high == g_high and last_g_low == g_low:
            stopping_reason = f"stopped earlier because no change in g(f,0,k) and g(f,1,k) occurred."
            ub_max_increase = 0
            break
        last_g_high, last_g_low = g_high, g_low

        new_ell = f.ite(g_high, g_low)
        if debug: print(f"size ell={new_ell.nodecount}", end=" ")

        new_ell_sc = new_ell.satcount()
        t_sc = new_ell_sc - last_ell_sc
        last_ell_sc = new_ell_sc

        d_result = rho(k)*t_sc / 2**f.ctx.varcount
        if debug: print(f"d result={d_result:.4f}", end=" ")
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - new_ell_sc / 2**f.ctx.varcount)
        if debug: print(f"max increase possible={ub_max_increase:.4f}", end=" ")

        if ub_max_increase <= cutoff:
            stopping_reason = f"stopped earlier because cannot improve above cutoff.\n" + \
                              f"current value: {result:.4f}, can be increased by "+\
                              f"{ub_max_increase:.4f} <= {cutoff:.4f}."
            break

        ub_max_increase = 0

    if debug: 
        print()
        print(stopping_reason)
        print(f"=== DONE ===")
    return result, result + ub_max_increase

@cache
def omega(f: BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return f.ctx.var(f.var).ite(high_tf, low_tf)
from ..formulas import Repr 
from functools import cache 
        
def blame(f: Repr, x: str, rho = lambda x: 1/(x+1), cutoff=1e-4, debug=False):
    if x not in f.vars: return 0, 0
    if debug: print(f"=== COMPUTING BLAME for {x} in {f} ===")

    @cache
    def g(f,c,k):
        if x not in f.vars:
            return type(f).false
        elif k == 0:
            return (f ^ f.flip(x)) & f.biimp(c)
        else:
            g_last = g(f,c,k-1)
            result = g_last
            for y in set(f.vars) - { x }:
                result |= g_last.flip(y)
            return result

    result = 0
    last_ell_ex = 0
    ub_max_increase = 1 
    last_g_high, last_g_low = type(f).false, type(f).false
    stopping_reason = "finished iteration."
    for k in range(len(f.vars)):
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = f"stopped because rho({k}) = 0"
            break

        g_high, g_low = g(f, type(f).true, k), g(f, type(f).false, k)
        if last_g_high == g_high and last_g_low == g_low:
            stopping_reason = f"stopped earlier because no change in g(f,0,k) and g(f,1,k) occurred."
            ub_max_increase = 0
            break
        last_g_high, last_g_low = g_high, g_low

        new_ell = f.ite(g_high, g_low)

        new_ell_ex = new_ell.expectation()
        t_ex = new_ell_ex - last_ell_ex
        last_ell_ex = new_ell_ex

        d_result = rho(k)*t_ex
        if debug: print(f"d result={d_result:.4f}", end=" ")
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - new_ell_ex)
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

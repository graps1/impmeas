from ..formulas import Table
from functools import cache 
        

def blame(f: Table, x: str, rho = lambda x: 1/(x+1), cutoff=1e-4, debug=False):
    # todo: this is (almost) the exact same code as for the BDD based approach...
    # can probably be merged...
    if debug: print(f"=== COMPUTING BLAME for {x} in Table with size {len(f.table)} ===")

    @cache
    def g(f,c,k):
        if x not in f.vars:
            return f.ctx.false
        elif k == 0:
            return f & ~f.flip(x) if c == 1 else ~f & f.flip(x)
        else:
            g_last = g(f,c,k-1)
            result = g_last
            for y in set(f.vars) - { x }:
                result |= g_last.flip(y)
            return result

    result = 0
    last_ell_sc = 0
    ub_max_increase = 1 
    last_g_high, last_g_low = f.ctx.false, f.ctx.false
    stopping_reason = "finished iteration."
    for k in range(len(f.vars)):
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = f"stopped because rho({k}) = 0"
            break

        g_high, g_low = g(f, 1, k), g(f, 0, k)
        if last_g_high == g_high and last_g_low == g_low:
            stopping_reason = f"stopped earlier because no change in g(f,0,k) and g(f,1,k) occurred."
            ub_max_increase = 0
            break
        last_g_high, last_g_low = g_high, g_low

        new_ell = (f&g_high) | (~f&g_low)

        new_ell_sc = new_ell.satcount()
        t_sc = new_ell_sc - last_ell_sc
        last_ell_sc = new_ell_sc

        d_result = rho(k)*t_sc / 2**len(f.vars)
        if debug: print(f"d result={d_result:.4f}", end=" ")
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - new_ell_sc / 2**len(f.vars))
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

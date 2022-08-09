from . import SharpSAT, Formula 
from functools import cache

def influence(f : Formula, x : str, solver : SharpSAT, debug=False):
    left = f.cofactor(x, False) 
    right = f.cofactor(x, True) 
    target = left ^ right
    return solver.satcount(target, debug=debug) / 2**(len(f.vars)-1)
    
def blame(f : Formula, x : str, solver : SharpSAT, 
    rho=lambda x: 1/(x+1), cutoff = 1e-4, debug=False):

    if debug: print(f"=== COMPUTING BLAME for {x} in Formula with size {len(str(f))} ===")

    @cache
    def g(f,h,k,Y):
        if x not in f.vars:
            return Formula.parse("0")
        elif k == 0:
            return (f ^ f.flip(x)) & ~(f ^ h)
        else:
            result = g(f,h,k-1,Y)
            for y in Y:
                Y_min_y = list(Y)
                Y_min_y.remove(y)
                result |= g(f.flip(y), h, k-1, tuple(Y_min_y))
            return result

    result = 0
    last_g = Formula.parse("0")
    ub_max_increase = 1 
    stopped_earlier = False
    varcount = len(f.vars)
    for k in range(varcount):
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
        new_g = g(f, f, k, tuple(f.vars - { x }))
        if last_g == new_g: # is this valid?
            break
        ell = new_g & ~last_g
        last_g = new_g
        d_result = rho(k)*solver.satcount(ell, debug=False) / 2**varcount
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - solver.satcount(new_g, debug=False) / 2**varcount)
        if debug: 
            print(f"k {k}", end=" ")
            print(f"size g {len(str(last_g))}", end=" ")
            print(f"size ell {len(str(ell))}", end=" ") 
            print(f"d result {d_result:.4f}", end=" ")
            print(f"max increase possible {ub_max_increase:.4f}")
    if not stopped_earlier: ub_max_increase = 0
    if debug: print(f"=== DONE ===")
    return result, result + ub_max_increase
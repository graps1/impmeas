from formulas import GPMC, Formula
from functools import cache
from itertools import count
from typing import Iterable, Union
from .utils import at_most_cnf

def resp_counts(f: Formula, x: str, solver: GPMC, debug=False) -> Iterable[int]:
    new_flip_vars = { f"__z_{y}": y for y in f.vars-{x} }
    replacements = { new_flip_vars[z]: Formula.parse(f"{z} ^{new_flip_vars[z]}") \
                     for z in new_flip_vars }
    f_ = f.replace(replacements)
    f_x = f_.flip(x)
    inner = (f & f_ & ~f_x) | (~f & ~f_ & f_x)

    cnf, sub2idx = inner.tseitin()
    new_flip_vars = { sub2idx[Formula.parse(p)] for p in new_flip_vars } # to index
    tseitin_vars = set(sub2idx.values()) - { sub2idx[Formula.parse(p)] for p in f.vars }

    # new_card_vars: set[int]
    # new_flip_vars: set[int]
    # sub2idx: dict[Formula,int]
    # tseitin_vars: set[int]

    for k in count(): 
        cnf_leqk, new_leqk_vars = at_most_cnf(k, new_flip_vars, max(max(c) for c in cnf)+1)
        exists = tseitin_vars | new_leqk_vars
        new_cnf = cnf + cnf_leqk
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")
        if debug: print(f"size of cnf: {len(new_cnf)}", end=" ")
        yield k, solver.satcount(cnf + cnf_leqk, exists=exists)

def influence(f: Formula, x: str, solver: GPMC, debug=False):
    high, low = f.cofactor(x, True), f.cofactor(x, False)
    return solver.satcount(high ^ low, debug=debug) / 2**(len(f.vars)-1)
    
def blame(f: Formula, x: str, solver: GPMC, rho=lambda x: 1/(x+1), cutoff = 1e-4, debug=False):
    if debug: print(f"=== COMPUTING BLAME for {x} in Formula with size {len(str(f))} ===")

    result = 0
    ub_max_increase = 1 
    stopped_earlier = False
    stopping_reason = "finished iteration."
    varcount = len(f.vars)
    last_ell_sc = 0
    for k, ell_satcount in resp_counts(f, x, solver, debug=debug):
        if k == varcount-1: break

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = "stopped because rho({k}) = 0"
            stopped_earlier = True
            break

        # if debug: print(f"size ell={len(new_ell)}", end=" ")

        t_sc = ell_satcount - last_ell_sc 
        last_ell_sc = ell_satcount

        d_result = rho(k)* (t_sc/ 2**varcount)
        if debug: print(f"d result={d_result:.4f}", end=" ") 

        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - ell_satcount / 2**varcount)
        if debug: print(f"max increase possible={ub_max_increase:.4f}",end=" ")

        if ub_max_increase <= cutoff:
            stopping_reason = "stopped earlier because cannot improve above cutoff.\n" \
                            + f"current value: {result:.4f}, can be increased by {ub_max_increase:.4f} <= {cutoff:.4f}."
            stopped_earlier = True
            break

    if debug:
        print()
        print(stopping_reason)
        print(f"=== DONE ===")
    if not stopped_earlier: ub_max_increase = 0
    return result, result + ub_max_increase
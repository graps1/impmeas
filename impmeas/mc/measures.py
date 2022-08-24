from formulas import Formula
from functools import cache
from itertools import count
from typing import Iterable, Union
from .utils import at_most_cnf

def resp_counts(f: Formula, x: str, debug=False) -> Iterable[int]:
    assert f.ctx.solver is not None
    solver = f.ctx.solver

    new_flip_vars = { f"__z_{y}": y for y in f.vars-{x} }
    replacements = { new_flip_vars[z]: f.ctx.parse(f"{z} ^ {new_flip_vars[z]}") \
                     for z in new_flip_vars }
    f_flip_vars = f.replace(replacements)
    f_flip_vars_x = f_flip_vars.flip(x)
    inner = (f & f_flip_vars & ~f_flip_vars_x) | (~f & ~f_flip_vars & f_flip_vars_x)

    cnf, sub2idx = inner.tseitin()
    new_flip_var_ids = { sub2idx[f.ctx.var(p)] for p in new_flip_vars } # to index
    orig_var_ids = { sub2idx[f.ctx.var(p)] for p in f.vars }
    all_var_ids = set(sub2idx.values())

    # new_card_vars: set[int]
    # new_flip_vars: set[int]
    # sub2idx: dict[Formula,int]
    # tseitin_vars: set[int]

    for k in count(): 
        cnf_leqk, new_leqk_vars = at_most_cnf(k, new_flip_var_ids, max(max(c) for c in cnf)+1)
        exists = (all_var_ids - orig_var_ids) | new_leqk_vars
        new_cnf = cnf + cnf_leqk
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")
        if debug: print(f"size of cnf: {len(new_cnf)}", end=" ")
        yield k, solver.satcount(cnf + cnf_leqk, exists=exists)

def influence(f: Formula, x: str, debug=False):
    f0, f1 = f.branch(x)
    return (f0 ^ f1).satcount() / 2**(len(f.vars)-1)
    
def blame(f: Formula, x: str, rho=lambda x: 1/(x+1), cutoff = 1e-4, debug=False):
    if debug: print(f"=== COMPUTING BLAME for {x} in Formula with size {len(str(f))} ===")

    result = 0
    ub_max_increase = 1 
    stopped_earlier = False
    stopping_reason = "finished iteration."
    varcount = len(f.vars)
    last_ell_sc = 0
    for k, ell_satcount in resp_counts(f, x, debug=debug):
        if k == varcount-1: break

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = "stopped because rho({k}) = 0"
            stopped_earlier = True
            break

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
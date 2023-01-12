from ..representation import Formula, get_pmc_solver 
from itertools import count
from typing import Iterable, Union
from .utils import at_most_cnf, totalizer

def resp_counts(f: Formula, x: str, debug=False, modified=False) -> Iterable[int]:
    max_varlength = max(len(v) for v in f.vars)
    new_flip_vars = { f"{'_'*max_varlength}z_{y}": y for y in f.vars-{x} }
    replacements = { new_flip_vars[z]: Formula.parse(("^", ("V", z), ("V", new_flip_vars[z]))) \
                     for z in new_flip_vars }
    f_flip_vars = f.replace(replacements)
    f_flip_vars_x = f_flip_vars.flip(x)

    if not modified:
        inner = (f & f_flip_vars & ~f_flip_vars_x) | (~f & ~f_flip_vars & f_flip_vars_x)
    else:
        inner = f_flip_vars ^ f_flip_vars_x

    cnf, var2idx, newvars = inner.tseitin(minimize_new_variables=True)
    new_flip_var_ids = { var2idx[p] for p in new_flip_vars } # to index
    orig_var_ids = { var2idx[p] for p in f.vars }
    all_var_ids = set(var2idx.values()) | set(newvars)

    for k in count(): 
        offset = max(max(abs(c) for c in cl) for cl in cnf)+1 
        # cnf_leqk, new_leqk_vars = at_most_cnf(k, new_flip_var_ids, offset)
        cnf_leqk, new_leqk_vars = totalizer(k, new_flip_var_ids, offset)
        exists = (all_var_ids - orig_var_ids) | new_leqk_vars
        new_cnf = cnf + cnf_leqk
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")
        if debug: print(f"size of cnf: {len(new_cnf)}", end=" ")
        yield k, get_pmc_solver().satcount(cnf + cnf_leqk, exists=exists)
    
def blame(f: Formula, x: str, rho=lambda x: 1/(x+1), cutoff = 0, modified=False, debug=False):
    if x not in f.vars: return 0, 0

    if debug: print(f"=== COMPUTING BLAME for {x} in Formula with size {len(str(f))} ===")

    result = 0
    ub_max_increase = 1 
    stopped_earlier = False
    stopping_reason = "finished iteration."
    varcount = len(f.vars)
    last_ell_sc = 0
    for k, ell_satcount in resp_counts(f, x, debug=debug, modified=modified):
        if k == varcount: break

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
            stopping_reason = f"stopped earlier because cannot improve above cutoff={cutoff:.4f}.\n" \
                            + f"current value: {result:.4f}, can only be increased by {ub_max_increase:.4f}."
            stopped_earlier = True
            break

    if debug:
        print()
        print(stopping_reason)
        print(f"=== DONE ===")
    if not stopped_earlier: ub_max_increase = 0
    return result, result + ub_max_increase
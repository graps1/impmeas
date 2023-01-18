from ..representation import PseudoBoolFunc, iter_assignments, BuddyNode, GPMC
import math
from typing import Callable, Union


def influence_cnf(cnf:list, x:int, solver: GPMC):
    # method from Traxler, 2009, Variable influences in conjunctive normal forms
    cnf_simp = [cl for cl in cnf if all((lit not in cl) or (-lit not in cl) for lit in cl)]
    vars_simp_cnf = max(max(abs(lit) for lit in cl) for cl in cnf_simp)
    e_w_x = solver.satcount(cnf_simp)*2**(-vars_simp_cnf)
    cnf_simp_wo_x = [[lit for lit in cl if abs(lit) != x] for cl in cnf_simp]
    vars_cnf_wo_x = max(max(abs(lit) for lit in cl) for cl in cnf_simp_wo_x)
    e_wo_x = solver.satcount(cnf_simp_wo_x)*2**(-vars_cnf_wo_x)
    return (e_w_x-e_wo_x)*2

def influence(f: PseudoBoolFunc, x: str) -> float:
    assert f.is_boolean
    if x not in f.vars: return 0
    return f.boolean_derivative(x).expectation()

def banzhaf(f: PseudoBoolFunc, x: str) -> float:
    assert isinstance(f,PseudoBoolFunc), type(f)
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    return f1.expectation() - f0.expectation()

def shapley(f: PseudoBoolFunc, x: str) -> float: 
    c = lambda k: 1/(len(f.vars)*math.comb(len(f.vars)-1,k))
    return expectation_of_contributions(f,x,c)

def expectation_of_contributions(f: PseudoBoolFunc, x: str, c: Callable[[int],float]) -> float:
    if x not in f.vars: return 0
    s = 0
    for ass in iter_assignments(set(f.vars)-{x}):
        marg = f[ass | {x:True}] - f[ass | {x:False}]
        s += c(len({y for y in ass if ass[y]}))*marg
    return s


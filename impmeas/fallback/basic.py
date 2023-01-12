from ..representation import PseudoBoolFunc, iter_assignments, BuddyNode
import math
from typing import Callable, Union

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


from ..formulas import Repr, iter_assignments, BuddyNode
import math
from typing import Callable, Union

def influence(f: Repr, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    return (f0^f1).expectation()

def banzhaf(f: Union[Repr, tuple[set[str], Callable[[dict[str,bool]],float]]], x: str) -> float:
    if isinstance(f,Repr):
        if x not in f.vars: return 0
        f0, f1 = f.branch(x)
        return f1.expectation() - f0.expectation()
    else: 
        n = len(f[0])
        c = lambda k: 1/2**(n-1)
        return expectation_of_contributions(f,x,c)

def shapley(f: Union[Repr, tuple[set[str], Callable[[dict[str,bool]],float]]], x: str) -> float: 
    n = len(f.vars) if isinstance(f, Repr) else len(f[0])
    c = lambda k: 1/(n*math.comb(n-1,k))
    return expectation_of_contributions(f,x,c)

def expectation_of_contributions(f: Union[Repr, tuple[set[str], Callable[[dict[str,bool]],float]]], x: str, c: Callable[[int],float]) -> float:
    if isinstance(f,Repr): vars = set(f.vars)
    else: vars, f = f
    if x not in vars: return 0
    s = 0
    for ass in iter_assignments(set(vars)-{x}):
        marg = f(ass | {x:True}) - f(ass | {x:False})
        s += c(len({y for y in ass if ass[y]}))*marg
    return s


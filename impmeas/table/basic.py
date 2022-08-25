from formulas import Table, iter_assignments
from math import comb

def influence(f: Table, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    return (f0 ^ f1).satcount() / 2**(len(f.vars)-1)

def banzhaf(f: Table, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    return (f1.satcount() - f0.satcount()) / 2**(len(f.vars)-1)

def shapley(f: Table, x: str) -> float: 
    if x not in f.vars: return 0
    n = len(f.vars)
    res = 0
    for Sass in iter_assignments(set(f.vars)-{x}):
        S = { y for y in Sass if Sass[y] }
        c = 1 / (comb(n-1, len(S))*n)
        res += c * (f[Sass | {x: True}] - f[Sass | {x: False}])
    return res

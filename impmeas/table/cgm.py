from typing import Iterable
from formulas import Table, iter_assignments
from functools import cache

@cache
def omega(f: Table) -> Table:
    if len(f.vars) == 0:
        return f
    else:
        x = next(iter(f.vars))
        low, high = f.branch(x)
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        xf = f.ctx.var(x)
        return xf & high_tf | ~xf & low_tf

@cache 
def upsilon(f: Table) -> Table:
    # upsilon_f(S) = forall ~S. exists S. f
    # thus:
    # - if x not in S: upsilon_f(S) = upsilon_f[x/0](S) & upsilon_f[x/1](S)
    # - if x in S: upsilon_f(S) = upsilon_(f[x/0] | f[x/1])(S - { x })
    if len(f.vars) == 0:
        return f
    else:
        x = next(iter(f.vars))
        low, high = f.branch(x)
        low_tf = upsilon(low) & upsilon(high)
        high_tf = upsilon(low | high)
        xf = f.ctx.var(x)
        return xf & high_tf | ~xf & low_tf

def hcgm(f: Table, S: set[str], rho = lambda x: 4*(0.5-x)**2) -> float:
    mean = 0
    for alpha in iter_assignments(S):
        f_alpha = f.cofactor(alpha)
        inner = f_alpha.satcount() / 2**len(f_alpha.vars)
        mean += rho(inner)
    mean = mean / 2**len(S)
    return mean

def bz_hcgm(f: Table, x: str, rho = lambda x: 4*(0.5-x)**2) -> float:
    if x not in f.vars: return 0
    result = 0
    for Sass in iter_assignments(set(f.vars)-{x}): 
        S = { y for y in Sass if Sass[y] } # assignment to set
        result += hcgm(f, S|{x}, rho) - hcgm(f, S, rho)
    return result / 2**(len(f.vars)-1)
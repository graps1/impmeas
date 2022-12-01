from ..formulas import Repr, iter_assignments
from functools import cache
from typing import Callable

@cache
def omega(f: Repr) -> Repr:
    if len(f.vars) == 0:
        return f
    else:
        x = next(iter(f.vars))
        low, high = f.branch(x)
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        xf = type(f).var(x)
        return xf.ite(high_tf, low_tf)

@cache 
def upsilon(f: Repr) -> Repr:
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
        xf = type(f).var(x)
        return xf.ite(high_tf, low_tf)

def hkr(f: Repr, kappa = lambda x: 4*(0.5-x)**2) -> Callable[[dict[str,bool]],float]:
    def ret(ass):
        S = {x for x in ass if ass[x]}
        mean = 0
        for alpha in iter_assignments(S):
            f_alpha = f.cofactor(alpha)
            mean += kappa(f_alpha.expectation())
        mean = mean / 2**len(S)
        return mean
    return ret
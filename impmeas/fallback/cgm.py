from ..representation import PseudoBoolFunc, iter_assignments, Table, add_buddy_delete_callback 
from functools import cache

@cache
def omega(f: PseudoBoolFunc) -> PseudoBoolFunc:
    assert f.is_boolean
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
def nu(f: PseudoBoolFunc) -> PseudoBoolFunc:
    assert f.is_boolean
    # upsilon_f(S) = forall ~S. exists S. f
    # thus:
    # - if x not in S: upsilon_f(S) = upsilon_f[x/0](S) & upsilon_f[x/1](S)
    # - if x in S: upsilon_f(S) = upsilon_(f[x/0] | f[x/1])(S - { x })
    if len(f.vars) == 0:
        return f
    else:
        x = next(iter(f.vars))
        low, high = f.branch(x)
        low_tf = nu(low) & nu(high)
        high_tf = nu(low | high)
        xf = type(f).var(x)
        return xf.ite(high_tf, low_tf)

def hkr(f: PseudoBoolFunc, kappa = lambda x: 4*(0.5-x)**2) -> Table:
    assert f.is_boolean
    ret = Table.zeros(list(f.vars))
    for ass in iter_assignments(f.vars):
        S = {x for x in ass if ass[x]}
        mean = 0
        for alpha in iter_assignments(S):
            f_alpha = f.cofactor(alpha)
            mean += kappa(f_alpha.expectation())
        mean = mean / 2**len(S)
        ret[ass] = mean
    return ret

add_buddy_delete_callback(omega.cache_clear)
add_buddy_delete_callback(nu.cache_clear)
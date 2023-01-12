from ..representation import PseudoBoolFunc, iter_assignments, add_buddy_delete_callback, BuddyNode
from functools import cache 
from itertools import combinations

def scs(f: PseudoBoolFunc, x: str, u: dict[str,bool], c=None) -> float:
    assert f.is_boolean
    assert x in f.vars
    if c is None: c = f[u]
    for level in range(len(f.vars)):
        for S in combinations(set(f.vars)-{x}, level):
            u_xor_S = u | { y: not u[y] for y in S }
            u_xor_S_xor_x = u_xor_S | { x: not u[x] }
            if f[u_xor_S] == c and f[u_xor_S_xor_x] != c:
                return level
    return float("inf")

def d(f: PseudoBoolFunc, u: dict[str,bool]) -> float:
    assert f.is_boolean
    for level in range(len(f.vars)+1):
        for S in combinations(set(f.vars), level):
            u_xor_S = u | { y: not u[y] for y in S }
            if f[u_xor_S] == 1:
                return level
    return float("inf")

def mscs(f: PseudoBoolFunc, x: str, u: dict[str,bool]) -> float:
    assert f.is_boolean
    return d(f.boolean_derivative(x),u)

@cache
def g(f,x,c,k):
    if k == 0:
        fx = f.flip(x)
        return f & ~fx if c else ~f & fx
    else:
        g_last = g(f,x,c,k-1)
        result = g_last
        for y in set(f.vars) - { x }:
            result |= g_last.flip(y)
        return result

@cache
def g_mod(f,x,k):
    if k == 0:
        return f.boolean_derivative(x)
    else:
        g_last = g_mod(f,x,k-1)
        result = g_last
        for y in set(f.vars) - { x }:
            result |= g_last.flip(y)
        return result
        
def blame(f: PseudoBoolFunc, x: str, rho = lambda x: 1/(x+1), cutoff=0, modified=False, debug=False):
    assert f.is_boolean
    if x not in f.vars: return 0, 0
    if debug: print(f"=== COMPUTING BLAME for {x} in {f} ===")

    result = 0
    last_ell_ex = 0
    ub_max_increase = 1 
    last_g_high, last_g_low = type(f).false, type(f).false # if not modified
    last_g = type(f).false # if modified
    stopping_reason = "finished iteration."
    for k in range(len(f.vars)):
        if debug and k > 0: print()
        if debug: print(f"k={k}", end=" ")

        # early stopping criteria
        if rho(k) == 0:
            stopping_reason = f"stopped because rho({k}) = 0"
            break

        if modified:
            new_g = g_mod(f,x,k)
            if last_g == new_g:
                stopping_reason = f"stopped earlier because no change in g_mod(f,x,k) occurred."
                ub_max_increase = 0
                break
            last_g = new_g
            new_ell = new_g
        else:
            g_high, g_low = g(f, x, True, k), g(f, x, False, k)
            if last_g_high == g_high and last_g_low == g_low:
                stopping_reason = f"stopped earlier because no change in g(f,x,0,k) and g(f,x,1,k) occurred."
                ub_max_increase = 0
                break
            last_g_high, last_g_low = g_high, g_low
            new_ell = f.ite(g_high, g_low)

        if debug and isinstance(new_ell, BuddyNode):
            print(f"bdd size={new_ell.nodecount}", end=" ")
        new_ell_ex = new_ell.expectation()
        t_ex = new_ell_ex - last_ell_ex
        last_ell_ex = new_ell_ex

        d_result = rho(k)*t_ex
        if debug: print(f"d result={d_result:.4f}", end=" ")
        result = result + d_result
        ub_max_increase = rho(k+1)*(1 - new_ell_ex)
        if debug: print(f"max increase possible={ub_max_increase:.4f}", end=" ")

        if ub_max_increase <= cutoff:
            stopping_reason = f"stopped earlier because cannot improve above cutoff={cutoff:.4f}.\n" + \
                              f"current value: {result:.4f}, can only be increased by {ub_max_increase:.4f}."
            break

        ub_max_increase = 0

    if debug: 
        print()
        print(stopping_reason)
        print(f"=== DONE ===")
    return result, result + ub_max_increase


add_buddy_delete_callback(g.cache_clear)
add_buddy_delete_callback(g_mod.cache_clear)
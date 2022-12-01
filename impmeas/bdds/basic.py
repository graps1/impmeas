from ..formulas import BuddyNode
from functools import cache
from math import comb

def influence(f: BuddyNode, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 =  f.branch(x)
    return (f1 ^ f0).satcount() / 2**(len(f.ctx.vars))

def banzhaf(f: BuddyNode, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    sc1 = f1.satcount()
    sc0 = f0.satcount()
    return (sc1 - sc0) / 2**(len(f.ctx.vars))

@cache
def wcount(f: BuddyNode, c = lambda k: k) -> float:
    # computed = { f.ctx.true: c(0), f.ctx.false: 0 }
    if f == f.ctx.true: return c(0)
    elif f == f.ctx.false: return 0
    else:
        cp1 = lambda k: c(k+1)
        left = wcount(f.low, c = c)
        right = wcount(f.high, c = cp1)
        return left + right


def shapley(f: BuddyNode, x: str) -> float:
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    n = len(f.ctx.vars)
    c = lambda k: 1/(n*comb(n-1, k))
    count1 = wcount(f1, c=c)
    count2 = wcount(f0, c=c)
    return count1 - count2
from formulas import BuddyNode
from functools import cache

@cache
def omega(f: BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return f.ctx.var(f.var).ite(high_tf, low_tf)
from ..formulas import BuddyNode
from functools import cache

@cache
def omega(f: BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return BuddyNode.var(f.var).ite(high_tf, low_tf)

@cache
def upsilon(f: BuddyNode):
    if f.var is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = upsilon(low) & upsilon(high)
        high_tf = upsilon(low | high)
        xf = BuddyNode.var(f.var)
        return xf.ite(high_tf, low_tf)
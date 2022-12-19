from ..formulas import BuddyNode, add_buddy_delete_callback
from functools import cache

@cache
def omega(f: BuddyNode):
    if f.topvar is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        return BuddyNode.var(f.topvar).ite(high_tf, low_tf)

@cache
def upsilon(f: BuddyNode):
    if f.topvar is None:
        return f
    else:
        low, high = f.low, f.high
        low_tf = upsilon(low) & upsilon(high)
        high_tf = upsilon(low | high)
        return BuddyNode.var(f.topvar).ite(high_tf, low_tf)

add_buddy_delete_callback(omega.cache_clear)
add_buddy_delete_callback(upsilon.cache_clear)
from formulas import Table 
from functools import cache

@cache
def omega(f: Table):
    if len(f.vars) == 0:
        return f
    else:
        x = next(iter(f.vars))
        low, high = f.branch(x)
        low_tf = omega(low & high)
        high_tf = omega(low) | omega(high)
        xf = f.ctx.var(x)
        return xf & high_tf | ~xf & low_tf
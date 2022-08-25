from formulas import BuddyNode

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
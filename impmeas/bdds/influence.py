from formulas import BuddyNode

def influence(f: BuddyNode, x: str, monotone_in_x=False):
    # computes the unnormalized influence (ie influence * 2**#variables)
    f0, f1 =  f.branch(x)
    if monotone_in_x:
        return (f1.satcount() - f0.satcount()) / 2**f.ctx.varcount
    else:
        return (f1 ^ f0).satcount() / 2**f.ctx.varcount
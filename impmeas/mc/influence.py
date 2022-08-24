from formulas import Formula

def influence(f: Formula, x: str, debug=False):
    f0, f1 = f.branch(x)
    return (f0 ^ f1).satcount() / 2**(len(f.vars)-1)
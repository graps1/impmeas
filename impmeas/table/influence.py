from formulas import Table

def influence(f: Table, x: str):
    f0, f1 = f.branch(x)
    return (f0 ^ f1).satcount() / 2**len(f.vars)
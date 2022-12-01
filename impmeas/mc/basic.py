from ..formulas import Formula

def influence(f: Formula, x: str, debug=False):
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    # removed_vars = f.vars - { x } - (f0.vars | f1.vars)
    sc = (f0 ^ f1).satcount() # * 2**len(removed_vars)
    return sc / 2**(len(f.vars) - 1)

def banzhaf(f: Formula, x: str, debug=False):
    if x not in f.vars: return 0
    f0, f1 = f.branch(x)
    sc1 = f1.satcount() # * 2**len(f.vars - { x } - f1.vars)
    sc0 = f0.satcount() # * 2**len(f.vars - { x } - f0.vars)
    return (sc1 - sc0) / 2**(len(f.vars)-1) 



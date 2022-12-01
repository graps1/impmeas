from . import mc, bdds, table, formulas
from .formulas import Repr, FormulaContext, BuddyContext, TableContext

str2value = {
    "I": { 
        TableContext: table.influence,
        FormulaContext: mc.influence,
        BuddyContext: bdds.influence,
    },
    "Blame": {
        TableContext: lambda f,x: table.blame(f,x,cutoff=0)[0],
        FormulaContext: lambda f,x: mc.blame(f,x,cutoff=0)[0],
        BuddyContext: lambda f,x: bdds.blame(f,x,cutoff=0)[0],
    },
    "Bz/CCGM": {
        FormulaContext: mc.banzhaf,
        BuddyContext: bdds.banzhaf,
        TableContext: table.banzhaf
    },
    "Sh/CCGM": {
        # "#SAT": mc.shapley,
        BuddyContext: bdds.shapley,
        TableContext: table.shapley
    },
    "Bz/DCGM": {
        BuddyContext: lambda f,x: bdds.banzhaf(table.omega(f), x),
        TableContext: lambda f,x: table.banzhaf(table.omega(f), x),
    },
    "Bz/RCGM": {
        BuddyContext: lambda f,x: bdds.banzhaf(table.upsilon(f), x),
        TableContext: lambda f,x: table.banzhaf(table.upsilon(f), x),
    },
    "Bz/QHCGM": {
        TableContext: lambda f,x: table.bz_hcgm(f, x, rho=lambda z: 4*(z-0.5)**2)
    }
}

def methods(val: str):
    assert val in str2value, f"importance value {val} not recognized. "+\
        f"choose one of {', '.join(str2value.keys())}."
    return str2value[val]

def value(val: str, f: Repr, x: str):
    via2value = methods(val)
    via = type(f.ctx)

    assert via in via2value, f"method {via} not applicable for "+\
        f"importance value {val}. choose one of "+\
        f"{', '.join(map(str, via2value.keys()))}."

    val = via2value[via]
    return val(f, x)



    
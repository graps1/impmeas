from . import mc, bdds, table, formulas
from .formulas import Repr, Table, Formula, BuddyNode

str2value = {
    "I": { 
        Table: table.influence,
        Formula: mc.influence,
        BuddyNode: bdds.influence,
    },
    "Blame": {
        Table: lambda f,x: table.blame(f,x,cutoff=0)[0],
        Formula: lambda f,x: mc.blame(f,x,cutoff=0)[0],
        BuddyNode: lambda f,x: bdds.blame(f,x,cutoff=0)[0],
    },
    "Bz/CCGM": {
        Formula: mc.banzhaf,
        BuddyNode: bdds.banzhaf,
        Table: table.banzhaf
    },
    "Sh/CCGM": {
        # "#SAT": mc.shapley,
        BuddyNode: bdds.shapley,
        Table: table.shapley
    },
    "Bz/DCGM": {
        BuddyNode: lambda f,x: bdds.banzhaf(table.omega(f), x),
        Table: lambda f,x: table.banzhaf(table.omega(f), x),
    },
    "Bz/RCGM": {
        BuddyNode: lambda f,x: bdds.banzhaf(table.upsilon(f), x),
        Table: lambda f,x: table.banzhaf(table.upsilon(f), x),
    },
    "Bz/QHCGM": {
        Table: lambda f,x: table.bz_hcgm(f, x, rho=lambda z: 4*(z-0.5)**2)
    }
}

def methods(val: str):
    assert val in str2value, f"importance value {val} not recognized. "+\
        f"choose one of {', '.join(str2value.keys())}."
    return str2value[val]

def value(val: str, f: Repr, x: str):
    via2value = methods(val)
    via = type(f)

    assert via in via2value, f"method {via} not applicable for "+\
        f"importance value {val}. choose one of "+\
        f"{', '.join(map(str, via2value.keys()))}."

    val = via2value[via]
    return val(f, x)


    
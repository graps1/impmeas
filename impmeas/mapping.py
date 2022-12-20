from . import PseudoBoolFunc, Formula, BuddyNode, Table
from . import mc, bdds, fallback
from .formulas import get_pmc_solver
from typing import Callable, Union

def influence(f: PseudoBoolFunc, x: str) -> float:
    return fallback.influence(f, x)

def blame(f: PseudoBoolFunc, x: str, rho=lambda x:1/(x+1), cutoff=1e-4,modified=False,debug=False) -> float:
    if get_pmc_solver() and type(f) ==Formula:
        method = mc.blame
    else: method = fallback.blame
    return method(f=f,x=x,rho=rho,cutoff=cutoff,modified=modified,debug=debug)[0]

def banzhaf(f: Union[PseudoBoolFunc,tuple[set[str], Callable[[dict[str, bool]],float]]], x: str) -> float:
    return fallback.banzhaf(f,x)

def shapley(f: Union[PseudoBoolFunc,tuple[set[str], Callable[[dict[str, bool]],float]]], x: str) -> float:
    return fallback.shapley(f,x)

def dominating_cgm(f: PseudoBoolFunc) -> PseudoBoolFunc:
    method = {
        BuddyNode: bdds.omega,
    }.get(type(f), fallback.omega)
    return method(f)

def rectifying_cgm(f: PseudoBoolFunc) -> PseudoBoolFunc:
    method = {
        BuddyNode: bdds.upsilon,
    }.get(type(f), fallback.nu)
    return method(f)

def hkr_cgm(f: PseudoBoolFunc, kappa = lambda x: 4*(0.5-x)**2) -> Table:
    return fallback.hkr(f,kappa)

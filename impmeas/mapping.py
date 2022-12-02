from . import Repr, Formula, BuddyNode
from . import mc, bdds, fallback
from .formulas import get_pmc_solver
from typing import Callable, Union

def influence(f: Repr, x: str) -> float:
    return fallback.influence(f, x)

def blame(f: Repr, x: str, rho=lambda x:1/(x+1), cutoff=1e-4,debug=False) -> float:
    if get_pmc_solver() and type(f) ==Formula:
        method = mc.blame
    else: method = fallback.blame
    return method(f,x,rho,cutoff,debug)[0]

def banzhaf(f: Union[Repr,tuple[set[str], Callable[[dict[str, bool]],float]]], x: str) -> float:
    return fallback.banzhaf(f,x)

def shapley(f: Union[Repr,tuple[set[str], Callable[[dict[str, bool]],float]]], x: str) -> float:
    return fallback.shapley(f,x)

def dominating_cgm(f: Repr) -> Repr:
    method = {
        BuddyNode: bdds.omega,
    }.get(type(f), fallback.omega)
    return method(f)

def rectifying_cgm(f: Repr) -> Repr:
    method = {
        BuddyNode: bdds.upsilon,
    }.get(type(f), fallback.upsilon)
    return method(f)

def hkr_cgm(f: Repr, kappa = lambda x: 4*(0.5-x)**2) -> tuple[set[str], Callable[[dict[str, bool]],float]]:
    return f.vars, fallback.hkr(f,kappa)

    
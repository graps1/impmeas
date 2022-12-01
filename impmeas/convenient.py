import random
from typing import Iterable
from .formulas import Table, iter_assignments

def random_assignment(vars: Iterable[str]) -> dict[str,bool]:
    return { x: bool(random.randint(0,1)) for idx,x in enumerate(vars) }

def random_subset(vars: Iterable[str]) -> set[str]:
    ass = random_assignment(vars)
    return { x for x in ass if ass[x] == 1 }

def random_table(vars: list[str]) -> Table:
    f = Table.zeros(vars)
    for ass in iter_assignments(vars): 
        f[ass] = bool(random.randint(0,1))
    return f

def random_k_cnf(n,m,k) -> tuple[list[list[int]], str]:
    cnf, formula = [], ""
    for ctr in range(m):
        clause = [(random.randint(0,1)*2-1)*random.randint(1,n) for _ in range(k)]
        inner = "(" + "|".join(f"x{idx}" if idx>0 else f"~x{-idx}" for idx in clause) + ")"
        formula = formula + "&" + inner if ctr > 0 else inner 
        cnf.append(clause)
    return cnf, formula
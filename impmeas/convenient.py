import random
from typing import Iterable
from .formulas import Table, iter_assignments

def random_assignment(vars: Iterable[str]) -> dict[str,bool]:
    return { x: bool(random.randint(0,1)) for idx,x in enumerate(vars) }

def random_subset(vars: Iterable[str]) -> set[str]:
    ass = random_assignment(vars)
    return { x for x in ass if ass[x] == 1 }

def set2ass(subset: set[str], domain: set[str]) -> dict[str,bool]:
    return { x:(x in subset) for x in domain }

def random_table(vars: list[str], monotone=False) -> Table:
    if len(vars) == 0:
        return Table.true if random.randint(0,1) else Table.false
    else:
        f0 = random_table(vars[1:], monotone=monotone)
        f1 = random_table(vars[1:], monotone=monotone)
    if monotone: f1 = f0|f1
    return Table.var(vars[0]).ite(f1,f0)

def random_module(X:list[str], Y:list[str], monotone=False) -> tuple[Table,Table,Table,Table]:
    f0 = random_table(Y)
    f1 = random_table(Y)
    if monotone: f1 = f1 | f0
    g = random_table(X)
    f = g.ite(f1,f0)
    return f,g,f1,f0

def random_k_cnf(n,m,k) -> tuple[list[list[int]], str]:
    cnf, formula = [], ""
    for ctr in range(m):
        clause = [(random.randint(0,1)*2-1)*random.randint(1,n) for _ in range(k)]
        inner = "(" + "|".join(f"x{idx}" if idx>0 else f"~x{-idx}" for idx in clause) + ")"
        formula = formula + "&" + inner if ctr > 0 else inner 
        cnf.append(clause)
    return cnf, formula
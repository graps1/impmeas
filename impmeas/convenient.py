import random
from typing import Iterable
from .representation import Table, iter_assignments

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

def random_k_cnf(n,m,k) -> tuple[list[list[int]], tuple]:
    cnf, formula = [], ""
    for ctr in range(m):
        clause = [(random.randint(0,1)*2-1)*random.randint(1,n) for _ in range(k)]
        inner = None
        for el in clause:
            val = ("V", f"x{el}") if el >= 0 else ("~", ("V", f"x{-el}"))
            if not inner: inner = val
            else: inner = ("|", inner, val)
        formula = ("&", formula, inner) if ctr > 0 else inner 
        cnf.append(clause)
    return cnf, formula

def parse_dimacs(dimacs) -> tuple[tuple, list, int, int]:
    formula, cnf, nvars, nclauses = None, [], None, None
    for el in dimacs.strip().split("\n"):
        if el.startswith("c"): continue
        elif el.startswith("p"):
            # vars clauses
            nvars = int(el.split()[2])
            nclauses = int(el.split()[3])
        else:
            clause = [ int(val) for val in el.split()[:-1] ]
            cnf.append(clause)
            inner = None
            for lit in clause:
                littpl = ("V", f"x{lit}") if lit > 0 else ("~", ("V", f"x{-lit}"))
                inner = ("|", inner, littpl) if inner else littpl
            formula = ("&", inner, formula) if formula else inner
    return formula, cnf, nvars, nclauses
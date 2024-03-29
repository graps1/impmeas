from typing import Iterable

def cnf2dimacs(cnf, projected=set()):
    # example output for input = ([{1,2,-3},{-2,3}], projected_set={1,2})
    # (represents the CNF (x1 & x2 & ~x3) | (~x2 & x3) w/ projected variables 1 and 2)
    # '''
    #     p cnf 3 2
    #     c p show 1 2 0
    #     c t pmc (...or c t mc for normal model count)
    #     1 2 -3 0
    #     -2 3 0
    # '''
    nr_vars = max(max(map(abs, clause)) for clause in cnf)
    is_projected = len(projected) >= 1
    ret = f"p cnf {nr_vars} {len(cnf)}\n"
    ret += "c t pmc\n" if is_projected else "c t mc\n"
    if is_projected: ret += "c p show " + " ".join(map(str, projected)) + " 0\n"
    for cl in cnf: ret += " ".join(map(str, cl)) + " 0\n"
    return ret

def iter_assignments(vars: Iterable[str]) -> Iterable[dict[str, int]]:
    vs_sorted = list(vars)[::-1]
    for ass in range(2**len(vs_sorted)):
        yield { v: bool((ass >> j) % 2) for j,v in enumerate(vs_sorted) }
 
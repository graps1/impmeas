from ..formulas import Formula

def at_most(k: int, X: set, new_var_prefix="__z_") -> tuple[Formula, set[str]]:
    assert k < len(X)

    n = len(X)
    X = list(X)
    Z = list(range(n*n))
    z = lambda i,j: f"{new_var_prefix}{Z[i+n*j]}"
    x = lambda i: X[i]

    f = Formula.parse(f"{z(0,0)} <-> {x(0)}")
    for l in range(1, n):
        f = f & Formula.parse(f"{z(0,l)} <-> {x(l)} | {z(0,l-1)}")
    for i in range(1, k+1):
        f = f & Formula.parse(f"{z(i,i)} <-> {x(i)} & {z(i-1,i-1)}")
        for l in range(i+1, n):
            f = f & Formula.parse(f"{z(i,l)} <-> {x(l)} & {z(i-1,l-1)} | {z(i,l-1)}")
    f = f & ~Formula.parse(z(k,n-1))
    return f, set(z(i,j) for i in range(k+1) for j in range(i, n))


def at_most_cnf(k: int, X: set, start_idx: int) -> tuple[list[list[int]], set]:
    assert k >= 0
    if k >= len(X): return [], set()

    n = len(X)
    X = list(X)
    Z = {(i,l) for i in range(k+1) for l in range(i,n)}
    Z = {k: j for j,k in enumerate(Z, start=start_idx)}
    z = lambda i,j: Z[(i,j)]
    x = lambda i: X[i]

    # z(0,0) <-> x(0)
    clauses = [[z(0,0), -x(0)], [-z(0,0), x(0)]] 
    for l in range(1, n):
        # z(0,l) <-> x(l) | z(0,l-1)
        clauses += [[x(l), z(0, l-1), -z(0, l)],\
                    [-x(l), z(0,l)], \
                    [-z(0,l-1), z(0,l)]]
    for i in range(1, k+1):
        # z(i,i) <-> x(i) & z(i-1,i-1)
        clauses += [[z(i,i), -x(i), -z(i-1,i-1)], \
                    [-z(i,i), z(i-1,i-1)], \
                    [-z(i,i), x(i)]]
        for l in range(i+1, n):
            # z(i,l) <-> x(l) & z(i-1,l-1) | z(i, l-1)
            clauses += [[-z(i,l), z(i-1,l-1), z(i,l-1)], \
                        [-z(i,l), x(l), z(i,l-1)], \
                        [z(i,l), -x(l), -z(i-1,l-1)], \
                        [z(i,l), -z(i,l-1)]]
    # ~z(k,n-1)
    clauses += [ [-z(k,n-1)] ]
    return clauses, set(Z.values())



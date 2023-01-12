from ..representation import Formula

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

def totalizer(k: int, X: set, start_idx: int) -> tuple[list[list[int]], set]:
    # cf. https://www.researchgate.net/profile/Yacine-Boufkhad/publication/221633097_Efficient_CNF_Encoding_of_Boolean_Cardinality_Constraints/links/0c960529848a5cd3ba000000/Efficient-CNF-Encoding-of-Boolean-Cardinality-Constraints.pdf
    assert k >= 0
    if k >= len(X): return [], set()

    clauses = []
    queue = [ { 0: i } for i in X ]
    new_var_offset = start_idx
    while len(queue) > 1:
        vars_left = queue.pop(0)
        vars_right = queue.pop(0)
        m_left = len(vars_left)
        m_right = len(vars_right)
        m = m_left + m_right
        vars_top = { i: i+new_var_offset for i in range(m) }
        new_var_offset += len(vars_top)

        for alpha in range(m_left+1):
            for beta in range(m_right+1):
                sigma = alpha+beta 
                C1 = []
                if sigma > 0 and m_left >= alpha and m_right >= beta:
                    if alpha > 0: C1 += [ -vars_left[alpha-1] ]   
                    if beta > 0: C1 += [ -vars_right[beta-1] ]
                    C1 += [ vars_top[sigma-1] ]
                    clauses += [ C1 ]
                C2 = []
                if sigma < m and 0 < alpha and 0 < beta:
                    if alpha < m_left: C2 += [ vars_left[alpha] ]
                    if beta < m_right: C2 += [ vars_right[beta] ]
                    C2 += [ -vars_top[sigma] ]
                    clauses += [ C2 ]

        queue.append( vars_top )

    # cardinality constraint <= k:
    vars_top = queue[0]
    clauses += [ [(-1)**(i>=k)*vars_top[i]] for i in range(len(X)) ]
    return clauses, set(range(start_idx, new_var_offset))


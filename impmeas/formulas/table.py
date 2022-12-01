from typing import Iterable
from .repr import Repr, ReprContext
from .utils import iter_assignments
import copy

class Table(Repr):
    def __init__(self, context: "TableContext", table: list[int], vars: list[str]):
        super().__init__(context)
        self.__table = table
        self.__vars = vars
        assert 2**len(self.vars) == len(self.table)

    @property 
    def table(self) -> list[int]:
        return self.__table

    # --- ABSTRACT METHODS ---

    @property 
    def vars(self) -> list[str]:
        return self.__vars

    def __call__(self, assignment: dict[str, bool]) -> bool:
        return self.table[self.assignment2idx(assignment)]

    def __hash__(self): 
        return tuple(self.table).__hash__() + tuple(self.vars).__hash__()

    def __copy__(self): 
        return Table(self.ctx, self.table.copy(), self.vars.copy())

    def cofactor(self, ass: dict[str, bool]) -> "Table": 
        new_vars = self.vars.copy()
        for x in ass: new_vars.remove(x)
        table = Table(self.ctx, [0 for _ in range(2**len(new_vars))], new_vars)
        for u in iter_assignments(new_vars):
            idx = table.assignment2idx(u)
            table.table[idx] = self(u | ass)
        return table

    def flip(self, x: str) -> "Table": 
        table = copy.copy(self)
        for ass in iter_assignments(self.vars):
            table[ass] = self(ass | { x: not ass[x] })
        return table

    def satcount(self):
        return sum(self.table)

    # --- END ABSTRACT METHODS ---

    def __setitem__(self, key, val):
        if isinstance(key, dict): 
            key = self.assignment2idx(key)
        self.table[key] = val

    def __getitem__(self, key):
        return self(key)

    def resort(self, new_vars: Iterable[str]) -> "Table":
        assert set(new_vars) == set(self.vars)
        cpy = copy.copy(self)
        for ass in iter_assignments(new_vars):
            cpy[ass] = self[ass]
        return cpy

    def assignment2idx(self, assignment: dict[str, bool]) -> int:
        table_index = 0
        for idx in range(len(self.vars)):
            v = self.vars[len(self.vars)-idx-1]
            if assignment[v]: table_index += 2**idx
        return table_index

    def __repr__(self):
        if self.ctx.print_mode == "table":
            ret = " ".join(self.vars) + " f" + "\n" + "-"*(len(self.vars)*2+1) 
            for ass in iter_assignments(self.vars):
                ret += "\n" + " ".join({True: "1", False: "0"}[ass[x]] for x in self.vars)
                ret += " " + str(int(self(ass)))
            ret += "\n"
        else:
            if self.satcount() == 0: return "0"
            elif self.satcount() == 2**len(self.vars): return "1"
            primes = self.prime_implicants()
            ret = " | ".join("".join(k if v else k+"'" for k,v in p.items()) for p in primes)
        return ret

    def __le__(self, other):
        return isinstance(other, Table) and \
               other.ctx == self.ctx and \
               set(other.vars) == set(self.vars) and \
               all(self[ass] <= other[ass] for ass in iter_assignments(self.vars))

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        return other <= self and self <= other

    def __ne__(self, other):
        return not (other == self)

    def prime_implicants(self) -> list[dict[str, int]]:
        assert 0 < self.satcount() < 2**len(self.vars), "function is constant!"

        us = [ ass for ass in iter_assignments(self.vars) if self[ass] == 1 ] 
        while True:
            # select resolvents
            marked = []
            for u1 in us:
                for u2 in us:
                    # check if they can be resolved, i.e. if there exists EXACTLY one variable 
                    # that occurs negatively in u1 and positively in u2 (or vice versa)
                    # and all other variables have the same value
                    if set(u1.keys()) != set(u2.keys()): continue 
                    difference = [ var for var in u1 if u1[var] != u2[var] ]
                    if len(difference) == 1:
                        # mark for resolution
                        marked.append((u1, u2, difference[0]))

            # if resolvents exists.... resolve. otherwise, stop.
            if len(marked) == 0:
                break

            for (res1, res2, targetvar) in marked:
                if res1 in us: us.remove(res1)
                if res2 in us: us.remove(res2)
                new = res1.copy()
                del new[targetvar]
                if new not in us: us.append(new)
        return us

class TableContext(ReprContext):
    def __init__(self, print_mode="table"):
        assert print_mode in ["table", "primes"], print_mode
        self.__print_mode = print_mode

    @property 
    def print_mode(self):
        return self.__print_mode

    @property
    def false(self) -> "Table": 
        return Table(self, [False], [])

    @property
    def true(self) -> "Table": 
        return Table(self, [True], [])

    def apply(self, op: str, *children) -> "Table":
        all_vars = list( set().union( *(set(c.vars) for c in children)) ) 
        new_table = Table(self, [0 for _ in range(2**len(all_vars))], all_vars)
        for ass in iter_assignments(all_vars):
            val = None
            if op == "~": val = not children[0](ass)
            elif op == "&": val = all(c(ass) for c in children)
            elif op == "|": val = any(c(ass) for c in children)
            elif op == "^": val = (children[0](ass) != children[1](ass))
            elif op == "->": val = (not children[0](ass) or children[1](ass))
            elif op == "<-": val = (children[0](ass) or not children[1](ass))
            elif op == "<->": val = (children[0](ass) == children[1](ass))
            new_table[ass] = val
        return new_table

    def var(self, x: str) -> "Table":
        return Table(self, [False, True], [x])

    def empty(self, vars: list[str]) -> "Table":
        return Table(self, [0 for _ in range(2**len(vars))], vars)

from typing import Iterable, Union
from .repr import Repr
from .utils import iter_assignments
import copy

PRINT_MODE = "primes"

class Table(Repr):
    def __init__(self, table: list[int], vars: list[str]):
        super().__init__()
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
        return Table(self.table.copy(), self.vars.copy())

    def replace(self, d: dict[str, str]):
        cpy_vars = self.vars.copy()
        for idx in range(len(self.vars)):
            if self.vars[idx] in d:
                cpy_vars[idx] = d[self.vars[idx]]
        assert len(self.vars) == len(set(cpy_vars)), "renaming must be a bijection!"
        return Table(self.table, cpy_vars)


    def cofactor(self, ass: dict[str, bool]) -> "Table": 
        new_vars = self.vars.copy()
        for x in ass: 
            if x in new_vars: 
                new_vars.remove(x)
        table = Table.zeros(new_vars)
        for u in iter_assignments(new_vars):
            idx = table.assignment2idx(u)
            table.table[idx] = self(u | ass)
        return table

    def flip(self, S: Union[str, set[str]]) -> "Table": 
        if isinstance(S,str): S = {S}
        table = copy.copy(self)
        for ass in iter_assignments(self.vars):
            table[ass] = self(ass | { x: not ass[x] for x in S })
        return table

    def expectation(self) -> float:
        return sum(self.table) / 2**len(self.vars)

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
        if PRINT_MODE == "table":
            ret = " ".join(self.vars) + " f" + "\n" + "-"*(len(self.vars)*2+1) 
            for ass in iter_assignments(self.vars):
                ret += "\n" + " ".join({True: "1", False: "0"}[ass[x]] for x in self.vars)
                ret += " " + str(int(self(ass)))
            ret += "\n"
        elif PRINT_MODE == "primes":
            if self.expectation() == 0: return "0"
            elif self.expectation() == 1: return "1"
            primes = self.prime_implicants()
            ret = " | ".join("".join(k if v else k+"'" for k,v in p.items()) for p in primes)
        else:
            raise Exception(f"PRINT_MODE must either be 'primes' or 'table' but is {PRINT_MODE}.")
        return ret

    def __le__(self, other):
        return isinstance(other, Table) and \
               set(other.vars) == set(self.vars) and \
               all(self[ass] <= other[ass] for ass in iter_assignments(self.vars))

    def __ge__(self, other):
        return other <= self

    def __eq__(self, other):
        return other <= self and self <= other

    def __ne__(self, other):
        return not (other == self)

    def prime_implicants(self) -> list[dict[str, int]]:
        assert 0 < self.expectation() < 1, "function is constant!"

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
        
    @classmethod
    @property
    def false(cls) -> "Table": 
        return cls([False], [])

    @classmethod
    @property
    def true(cls) -> "Table": 
        return cls([True], [])

    @classmethod
    def zeros(cls, vars: list[str]) -> "Table":
        return cls([0 for _ in range(2**len(vars))], vars)

    @classmethod
    def apply(cls, op: str, *children) -> "Table":
        all_vars = list( set().union( *(set(c.vars) for c in children)) ) 
        new_table = cls.zeros(all_vars)
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

    @classmethod
    def var(cls, x: str) -> "Table":
        return cls([False, True], [x])

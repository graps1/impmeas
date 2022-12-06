from typing import Iterable, Union
from .repr import PseudoBoolFunc
from .utils import iter_assignments
import copy

class Table(PseudoBoolFunc):
    MUST_ALWAYS_BE_BOOLEAN = False

    def __init__(self, table: list[int], vars: list[str], print_mode="primes"):
        super().__init__()
        self.__table = table
        self.__vars = vars
        self.__print_mode = print_mode
        assert 2**len(self.vars) == len(self.__table)

    def set_print_mode(self, mode):
        assert mode in ["table", "primes"]
        self.__print_mode = mode

    def __getitem__(self, key):
        return self.__table[self.assignment2idx(key)]

    def __hash__(self): 
        return tuple(self.__table).__hash__() + tuple(self.vars).__hash__()

    def __copy__(self): 
        return Table(self.__table.copy(), self.vars.copy())

    @property
    def is_boolean(self):
        return all(c in [0,1] for c in self.__table)

    @property
    def vars(self) -> Iterable[str]: 
        return self.__vars

    def cofactor(self, ass: dict[str, bool]) -> "Table": 
        new_vars = [x for x in self.vars if x not in ass]
        table = Table.zeros(new_vars)
        for u in iter_assignments(new_vars):
            table[u] = self[u | ass]
        return table

    def flip(self, S: Union[str, set[str]]) -> "Table": 
        if isinstance(S,str): S = {S}
        table = copy.copy(self)
        for ass in iter_assignments(self.vars):
            table[ass] = self[ass | { x: not ass[x] for x in S }]
        return table
        
    @classmethod
    @property
    def false(cls) -> "Table": 
        return Table([False], [])

    @classmethod
    @property
    def true(cls) -> "Table": 
        return Table([True], [])

    @classmethod
    def _apply(cls, op: str, *children) -> "Table":
        assert all( isinstance(c,PseudoBoolFunc) or isinstance(c,float) or isinstance(c,int) for c in children ) 
        all_vars = list( set().union( *(set(c.vars) for c in children if isinstance(c, PseudoBoolFunc) )) ) 
        new_table = Table.zeros(all_vars)
        children_are_boolean = all(c.is_boolean if isinstance(c,PseudoBoolFunc) else c in [0,1] for c in children)
        for ass in iter_assignments(all_vars):
            vals = [ c[ass] if isinstance(c, PseudoBoolFunc) else c for c in children ]
            val = None
            if op == "+": val = vals[0]+vals[1]
            elif op == "-": val = -vals[0]
            elif op == "*": val = vals[0]*vals[1]
            elif op == "**": val = vals[0]**vals[1]
            elif op == "abs": val = abs(vals[0])
            elif children_are_boolean:
                if op == "~": val = not vals[0]
                elif op == "&": val = vals[0] and vals[1]
                elif op == "|": val = vals[0] or vals[1]
                elif op == "^": val = vals[0] != vals[1]
                elif op == "->": val = not vals[0] or vals[1]
                elif op == "<-": val = vals[0] or not vals[1]
                elif op == "<->": val = vals[0] == vals[1]
                else: raise Exception(f"operation {op} not applicable if all operands are Boolean functions.")
            else: raise Exception(f"operation {op} not applicable.")
            new_table[ass] = val
        return new_table

    @classmethod
    def var(cls, x: str) -> "Table":
        return Table([False, True], [x])

    def expectation(self) -> float:
        return sum(self.__table) / 2**len(self.vars)

    # --- END ABSTRACT METHODS ---

    def replace(self, d: dict[str, str]):
        cpy_vars = self.vars.copy()
        for idx in range(len(self.vars)):
            if self.vars[idx] in d:
                cpy_vars[idx] = d[self.vars[idx]]
        assert len(self.vars) == len(set(cpy_vars)), "renaming must be a bijection!"
        return Table(self.__table, cpy_vars)

    def __setitem__(self, key, val):
        if isinstance(key, dict): 
            key = self.assignment2idx(key)
        self.__table[key] = val

    # def resort(self, new_vars: Iterable[str]) -> "PseudoBoolFunc":
    #     assert set(new_vars) == set(self.vars)
    #     cpy = copy.copy(self)
    #     for ass in iter_assignments(new_vars):
    #         cpy[ass] = self[ass]
    #     return cpy

    def assignment2idx(self, assignment: dict[str, bool]) -> int:
        table_index = 0
        for idx in range(len(self.vars)):
            v = self.vars[len(self.vars)-idx-1]
            if assignment[v]: table_index += 2**idx
        return table_index

    def __repr__(self):
        if self.__print_mode == "table" or not self.is_boolean:
            ret = " ".join(self.vars) + " f" + "\n" + "-"*(len(self.vars)*2+1) 
            for ass in iter_assignments(self.vars):
                ret += "\n" + " ".join({True: "1", False: "0"}[ass[x]] for x in self.vars)
                ret += f" {float(self[ass]):.5}"
            ret += "\n"
        elif self.__print_mode == "primes":
            if self.expectation() == 0: return "0"
            elif self.expectation() == 1: return "1"
            primes = self.prime_implicants()
            ret = " | ".join("".join(k if v else k+"'" for k,v in p.items()) for p in primes)
        else:
            raise Exception(f"print_mode must either be 'primes' or 'table' but is {self.__print_mode}.")
        return ret

    @classmethod
    def zeros(cls, vars: list[str]) -> "Table":
        return Table([0 for _ in range(2**len(vars))], vars)

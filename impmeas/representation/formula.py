from .gpmc import GPMC
from .repr import PseudoBoolFunc
from .formula_parser import OPERATIONS, PRECEDENCE
from typing import Union
import copy

_SIMP_RULES = [
    ("~0", "1"),
    ("~1", "0"),
    ("~~A", "A"),

    ("~A & A", "0"),
    ("A & ~A", "0"),
    ("A & A", "A"),
    ("1 & A", "A"),
    ("A & 1", "A"),
    ("0 & A", "0"),
    ("A & 0", "0"),

    ("A | ~A", "1"),
    ("~A | A", "1"),
    ("A | A", "A"),
    ("0 | A", "A"),
    ("A | 0", "A"),
    ("1 | A", "1"),
    ("A | 1", "1"),

    ("A ^ A", "0"),
    ("A ^ ~A", "1"),
    ("~A ^ A", "1"),
    ("0 ^ A", "A"),
    ("A ^ 0", "A"),
    ("1 ^ A", "~A"),
    ("A ^ 1", "~A"),

    ("A -> ~A", "~A"),
    ("~A -> A", "A"),
    ("A -> A", "1"),
    ("0 -> A", "1"),
    ("A -> 0", "~A"),
    ("1 -> A", "A"),
    ("A -> 1", "1"),

    ("A <- ~A", "A"),
    ("~A <- A", "~A"),
    ("A <- A", "1"),
    ("0 <- A", "~A"),
    ("A <- 0", "1"),
    ("1 <- A", "1"),
    ("A <- 1", "A"),

    ("A <-> A", "1"),
    ("A <-> ~A", "0"),
    ("~A <-> A", "0"),
    ("0 <-> A", "~A"),
    ("A <-> 0", "~A"),
    ("1 <-> A", "A"),
    ("A <-> 1", "A"),
]

class Formula(PseudoBoolFunc):
    MUST_ALWAYS_BE_BOOLEAN = True

    def __init__(self, op=None, *children):
        super().__init__()

        assert op in ["C","V"] or op in OPERATIONS, op

        if op in ["C", "V"]: assert len(children)==1 and isinstance(children[0], str), (op, children)
        else: assert all(isinstance(c,Formula) for c in children), (op, children)

        if op == "~": assert len(children)==1, (op, children)
        elif op in ["->", "<-", "<->"]: assert len(children) == 2, (op, children)
        elif op in ["|", "&", "^"]: assert len(children) >= 2, (op, children)

        self.__op = op 
        self.__children = tuple(children)
        self.__str_repr = None

    # --- ABSTRACT METHODS ---

    def __getitem__(self, assignment: dict[str, bool]) -> bool:
        if self.op == "V": return assignment[self.c1]
        elif self.op == "C": return {"0": False, "1": True}[self.c1]
        elif self.op == "~": return not self.c1[assignment]
        else: # 2-ary operation
            left, right = self.children
            if self.op == "&":
                return left[assignment] and right[assignment]
            elif self.op == "|":
                return left[assignment] or right[assignment]
            elif self.op == "<->":
                return left[assignment] == right[assignment]
            elif self.op == "->":
                return not left[assignment] or right[assignment]
            elif self.op == "<-":
                return left[assignment] or not right[assignment]
            elif self.op == "^":
                return left[assignment] != right[assignment]

    def __hash__(self) -> int:
        return (self.op, self.children).__hash__()

    def __copy__(self) -> "Formula":
        return Formula(self.op, *(copy.copy(c) for c in self.children))

    def is_boolean(self):
        return True

    @property     
    def vars(self) -> set[str]:
        if self.op == "V": return { self.c1 }
        elif self.op == "C": return set()
        else: 
            ret = set()
            for c in self.children: ret |= c.vars
            return ret

    def cofactor(self, ass: dict[str, int]) -> "Formula":
        if self.op == "V" and self.c1 in ass: 
            return Formula.true if ass[self.c1] else Formula.false
        elif self.op in ["V", "C"]: 
            return copy.copy(self)
        else: 
            return Formula(self.op, *(c.cofactor(ass) for c in self.children))

    def flip(self, S : Union[str,set[str]]) -> "Formula":
        if isinstance(S, str): S = {S}
        if self.op == "V" and self.c1 in S: return Formula("~", self)
        elif self.op in ["V", "C"]: return copy.copy(self)
        else: return Formula(self.op, *(c.flip(S) for c in self.children))

    @classmethod
    @property
    def false(cls) -> "Formula": 
        return cls("C", "0")

    @classmethod
    @property
    def true(cls) -> "Formula": 
        return cls("C", "1")

    @classmethod
    def _apply(cls, op: str, *children) -> "Formula":
        return Formula(op, *children)

    @classmethod
    def var(cls, x: str) -> "Formula": 
        return cls("V", x)

    ## END ABSTRACT
    ## THE FOLLOWING IS OVERWRITTEN:

    def expectation(self, exists=set()) -> float:
        simp = self.simplify()
        if not PMC_SOLVER: 
            print("PMC_SOLVER not instantiated. iterating over all assignments.")
            return super(Formula, simp).expectation()
        if simp == Formula.false: return 0
        if simp == Formula.true: return 1

        cnf, var2idx, newvars = simp.tseitin() # create cnf encoding

        # existentially quantifies new tseitin variables + those that are explicitly specified
        # we have: tseitin vars ids = all_vars_ids - orig_vars_ids
        exists_ids = set(newvars) | { var2idx[x] for x in exists }
        sc = PMC_SOLVER.satcount(cnf, exists=exists_ids)
        return  sc / 2**len(simp.vars)

    def __eq__(self, other) -> bool: # structural equality!
        if not isinstance(other, Formula):
            raise NotImplementedError()
        if self.op != other.op: 
            return False
        if self.op in ["V", "C"]:
            return self.children[0] == other.children[0] 
        else: 
            return all(c1 == c2 for c1,c2 in zip(self.children, other.children))

    def __ge__(self, other): raise NotImplementedError()
    def __le__(self, other): raise NotImplementedError()

    def equivalent(self, other):
        if not isinstance(other, Formula):
            raise NotImplementedError()
        else:
            return (self ^ other).expectation() == 0

    # --- END ABSTRACT METHODS ---

    def __len__(self) -> int:
        if self.op in ["V", "C"]: return 1
        else: return 1 + sum(map(len, self.children))

    def treestr(self, indent=0) -> str:
        ind = "  "*indent
        if self.op in ["C", "V"]: return ind + self.c1
        else: return ind + self.op + "\n" +\
                     "\n".join(c.treestr(indent+1) for c in self.children)

    @property
    def op(self) -> str: 
        return self.__op

    @property
    def c1(self) -> Union["Formula", str]: 
        return self.__children[0]
    
    @property
    def c2(self) -> Union["Formula", str]: 
        return self.__children[1]

    @property 
    def children(self) -> tuple[Union["Formula", str]]: 
        return self.__children

    def __repr__(self):
        if self.__str_repr is not None:
            return self.__str_repr

        if self.op in ["C", "V"]: 
            self.__str_repr = self.c1
        elif self.op == "~": 
            if self.c1.op in ["C", "V"]: self.__str_repr = "~" + str(self.c1)
            else: self.__str_repr = "~(" + str(self.c1) + ")"
        else:
            child_strings = []
            for c in self.children: 
                if PRECEDENCE[c.op] >= PRECEDENCE[self.op]:
                    child_strings.append( "(" + str(c) + ")" )
                else:
                    child_strings.append(str(c))
            self.__str_repr = f"{self.op}".join(child_strings)
        return str(self)

    def is_applicable(self, template: "Formula") -> dict[str, "Formula"]:
        def rec(formula: "Formula", temp: "Formula", replacement: dict):
            if temp.op == "V": 
                if temp.c1 not in replacement:
                    replacement[temp.c1] = formula 
                return formula == replacement[temp.c1]
            elif temp.op == "C":
                return temp == formula
            else:
                return temp.op == formula.op and \
                       len(formula.children) == len(temp.children) and \
                       all( rec(f, t, replacement) for f,t in zip(formula.children, temp.children) )
        replacement = {}
        result = rec(self, template, replacement)
        if result: return replacement 
        else: return None

    def simplify(self) -> "Formula":
        if self.op in ["C", "V"]: 
            return self
        else:
            self_simplified = Formula(self.op, *(c.simplify() for c in self.children))
            while True:
                rule_applicable = False
                for rule, result in SIMP_RULES:
                    if (replacement := self_simplified.is_applicable(rule)) is not None:
                        self_simplified = result.replace(replacement)                    
                        rule_applicable = True 
                        break
                if not rule_applicable: break
            return self_simplified 
    
    def replace(self, d: dict[str, Union["Formula", str]]):
        if self.op == "V" and self.c1 in d: 
            repl = d[self.c1]
            if isinstance(repl, str): repl = Formula.parse(repl)
            return copy.copy(repl)
        elif self.op in ["V", "C"]: return copy.copy(self)
        else: return Formula(self.op, *(c.replace(d) for c in self.children))

    def tseitin(self, minimize_new_variables=False) -> tuple[list[list], dict[str, int]]:
        # formula = self.simplify()
        if self == Formula.false or self == Formula.true:
            return [], {}

        vars2idx = { v: idx+1 for idx, v in enumerate(self.vars) }
        
        if minimize_new_variables: 
            formula2tseitinvar = dict()
        
        newvars = [ max(vars2idx.values())+1 ]
        def _tseitin(formula: Formula, cnf: list):
            op = formula.op
            if op == "C": 
                raise Exception(f"formula cannot contain 0s or 1s. Simplify first.")
            elif op == "V": 
                return vars2idx[formula.c1]
            else:
                if minimize_new_variables and formula in formula2tseitinvar:
                    C = formula2tseitinvar[formula]
                else:
                    C = newvars[-1] 
                    newvars.append(newvars[-1]+1)
                    if minimize_new_variables:
                        formula2tseitinvar[formula] = C
                A = _tseitin(formula.c1, cnf)
                if op == "~":
                    cnf += [[-C, -A], [C, A]]
                else:
                    B = _tseitin(formula.c2, cnf)
                    if op == "<->": cnf += [[-A, -B, C], [A, B, C], [A, -B, -C], [-A, B, -C]]
                    elif op == "<-": cnf += [[A, -B, -C], [-A, C], [B, C]]
                    elif op == "->": cnf += [[-A, B, -C], [A, C], [-B, C]]
                    elif op == "^": cnf += [[-C, -A, -B], [-C, A, B], [C, -A, B], [C, A, -B]]
                    elif op == "&": cnf += [[-A, -B, C], [A, -C], [B, -C]]
                    elif op == "|": cnf += [[A, B, -C], [-A, C], [-B, C]]
                    else: raise Exception(f"operation {op} unknown!")
                return C
        
        cnf = []
        topid = _tseitin(self, cnf)
        return [[topid]]+cnf, vars2idx, newvars 


SIMP_RULES = [ (Formula.parse(l), Formula.parse(r)) for l,r in _SIMP_RULES ]
PMC_SOLVER: "GPMC" = None

def set_pmc_solver(solver : GPMC):
    global PMC_SOLVER
    PMC_SOLVER = solver

def get_pmc_solver():
    return PMC_SOLVER
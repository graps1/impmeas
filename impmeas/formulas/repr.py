from abc import ABC, abstractmethod
from . import formula_parser
from .utils import iter_assignments
from typing import Union, Iterable

class PseudoBoolFunc:
    MUST_ALWAYS_BE_BOOLEAN = False

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self): 
        raise NotImplementedError()

    @abstractmethod
    def __copy__(self): 
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_boolean(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def vars(self) -> Iterable[str]: 
        raise NotImplementedError()

    @abstractmethod
    def cofactor(self, ass: dict[str, bool]) -> "PseudoBoolFunc": 
        raise NotImplementedError()

    @abstractmethod
    def flip(self, S: Union[str, set[str]]) -> "PseudoBoolFunc": 
        raise NotImplementedError()

    @classmethod
    @property
    @abstractmethod 
    def false(cls) -> "PseudoBoolFunc": 
        raise NotImplementedError()

    @classmethod
    @property
    @abstractmethod 
    def true(cls) -> "PseudoBoolFunc": 
        raise NotImplementedError()

    @classmethod
    @abstractmethod 
    def _apply(cls, op: str, *children) -> "PseudoBoolFunc":
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def var(cls, x: str) -> "PseudoBoolFunc":
        raise NotImplementedError()

    ## END ABSTRACT METHODS
    ## THE FOLLOWING MAY BE OVERWRITTEN

    def expectation(self) -> float:
        return sum( self[u] for u in iter_assignments(self.vars) ) / 2**len(self.vars)

    def __le__(self, other):
        if isinstance(other,float) or isinstance(other,int):
            return all(self[ass] <= other for ass in iter_assignments(self.vars))
        elif isinstance(other, PseudoBoolFunc):
            return all(self[ass] <= other[ass] for ass in iter_assignments(set(self.vars)|set(other.vars)))
        else:
            return False

    def __ge__(self, other):
        if isinstance(other,float) or isinstance(other,int):
            return all(self[ass] >= other for ass in iter_assignments(self.vars))
        elif isinstance(other, PseudoBoolFunc):
            return all(self[ass] >= other[ass] for ass in iter_assignments(set(self.vars)|set(other.vars)))
        else:
            return False

    ## THE REMAINDER IS GOOD

    def __eq__(self, other): return other <= self and self <= other
    def __ne__(self, other): return not (other == self)

    def prime_implicants(self) -> list[dict[str, int]]:
        assert self.is_boolean
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

    def branch(self, *vars: list[str]) -> list["PseudoBoolFunc"]:
        for ass in iter_assignments(vars):
            yield self.cofactor(ass)

    def forall(self, S:set[str]) -> "PseudoBoolFunc":
        assert self.is_boolean
        if len(S) == 0:
            return self
        else:
            top = next(iter(S))
            f0,f1 = self.branch(top)
            return (f0 & f1).forall(S-{top})

    def exists(self, S:set[str]) -> "PseudoBoolFunc":
        assert self.is_boolean
        return ~(~self).forall(S)

    def derivative(self, x:str)->"PseudoBoolFunc":
        assert not type(self).MUST_ALWAYS_BE_BOOLEAN
        f0,f1 = self.branch(x)
        return f1-f0

    def boolean_derivative(self, x:str) -> "PseudoBoolFunc":
        assert self.is_boolean
        f0,f1 = self.branch(x)
        return f1^f0

    ## PSEUDO BOOLEAN OPERATIONS
    def __add__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return type(self)._apply("+", self, other)
    def __radd__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return self.__add__(other)
    def __neg__(self) -> "PseudoBoolFunc": return type(self)._apply("-", self)
    def __sub__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return self + (-other)
    def __rsub__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return -self.__sub__(other)
    def __pow__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return type(self)._apply("**", self, other)
    def __mul__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return type(self)._apply("*", self, other)
    def __rmul__(self, other: Union["PseudoBoolFunc", int, float]) -> "PseudoBoolFunc": return self.__mul__(other)
    def __abs__(self) -> "PseudoBoolFunc": return type(self)._apply("abs", self)

    ## BOOLEAN OPERATIONS
    def __or__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("|", self, other)
    def __ror__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return self.__or__(other)
    def __and__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("&", self, other)
    def __rand__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return self.__and__(other)
    def __xor__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("^", self, other)
    def __rxor__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return self.__xor__(other)
    def __rshift__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("->", self, other)
    def __rrshift__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return self.__lshift__(other)
    def __lshift__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("<-", self, other)
    def __rlshift__(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return self.__rshift__(other)
    def __invert__(self): return type(self)._apply("~", self)
    def biimp(self, other: Union["PseudoBoolFunc", bool]) -> "PseudoBoolFunc": return type(self)._apply("<->", self, other)
    def ite(self, o1: Union["PseudoBoolFunc",bool], o2: Union["PseudoBoolFunc",bool]) -> "PseudoBoolFunc": return self & o1 | ~self & o2

    @classmethod
    def parse(cls, formula: str) -> "PseudoBoolFunc":
        def rec(parsed):
            op, args = parsed[0], parsed[1:]
            if op == "C" and args[0] == "0": return cls.false
            elif op == "C" and args[0] == "1": return cls.true
            elif op == "V": return cls.var(args[0])
            else: return cls._apply(op, *(rec(a) for a in args))
        return rec(formula_parser.parse(formula))
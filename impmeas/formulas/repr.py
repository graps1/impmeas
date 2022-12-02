from abc import ABC, abstractmethod
from . import formula_parser
from .utils import iter_assignments
from typing import Union

class Repr(ABC):

    @abstractmethod
    def __hash__(self): 
        raise NotImplementedError()

    @abstractmethod
    def __call__(self, assignment: dict[str, bool]) -> bool: 
        raise NotImplementedError()

    @abstractmethod
    def __copy__(self): 
        raise NotImplementedError()

    @abstractmethod
    def cofactor(self, ass: dict[str, bool]) -> "Repr": 
        raise NotImplementedError()

    @abstractmethod
    def flip(self, S: Union[str, set[str]]) -> "Repr": 
        raise NotImplementedError()

    @property
    @abstractmethod 
    def vars(self) -> set[str]: 
        raise NotImplementedError()

    def forall(self, S:set[str]) -> "Repr":
        if len(S) == 0:
            return self
        else:
            top = next(iter(S))
            f0,f1 = self.branch(top)
            return (f0 & f1).forall(S-{top})

    def exists(self, S:set[str]) -> "Repr":
        return ~(~self).forall(S)

    def derivative(self, x:str) -> "Repr":
        f0,f1 = self.branch(x)
        return f1^f0

    def expectation(self) -> float:
        return sum( self(u) for u in iter_assignments(self.vars) ) / 2**len(self.vars)

    def branch(self, *vars: list[str]) -> list["Repr"]:
        for ass in iter_assignments(vars):
            yield self.cofactor(ass)

    def __or__(self, other: "Repr") -> "Repr": return type(self).apply("|", self, other)
    def __and__(self, other: "Repr") -> "Repr": return type(self).apply("&", self, other)
    def __xor__(self, other: "Repr") -> "Repr": return type(self).apply("^", self, other)
    def __rshift__(self, other: "Repr") -> "Repr": return type(self).apply("->", self, other)
    def __lshift__(self, other: "Repr") -> "Repr": return type(self).apply("<-", self, other)
    def __invert__(self): return type(self).apply("~", self)
    def biimp(self, other: "Repr") -> "Repr": return type(self).apply("<->", self, other)
    def ite(self, o1: "Repr", o2: "Repr") -> "Repr": return self & o1 | ~self & o2

    @classmethod
    @abstractmethod
    def var(cls, x: str) -> "Repr": 
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def false(cls) -> "Repr": 
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def true(cls) -> "Repr": 
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def apply(cls, op: str, *children) -> "Repr":
        raise NotImplementedError() 

    @classmethod
    def parse(cls, formula: str) -> "Repr":
        def rec(parsed):
            op, args = parsed[0], parsed[1:]
            if op == "C" and args[0] == "0": return cls.false
            elif op == "C" and args[0] == "1": return cls.true
            elif op == "V": return cls.var(args[0])
            else: return cls.apply(op, *(rec(a) for a in args))
        return rec(formula_parser.parse(formula))
from abc import ABC, abstractmethod
from . import formula_parser
from .utils import iter_assignments

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
    def flip(self, x: str) -> "Repr": 
        raise NotImplementedError()

    @property
    @abstractmethod 
    def vars(self) -> set[str]: 
        raise NotImplementedError()

    @abstractmethod 
    def satcount(self) -> int:
        raise NotImplementedError()

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

    @classmethod
    @abstractmethod
    def var(cls, x: str) -> "Repr": 
        raise NotImplementedError()

    @property
    @classmethod
    @abstractmethod
    def false(cls) -> "Repr": 
        raise NotImplementedError()

    @property
    @classmethod
    @abstractmethod
    def true(cls) -> "Repr": 
        raise NotImplementedError()

    @property
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

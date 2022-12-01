from abc import ABC, abstractmethod
from . import parser
from .utils import iter_assignments

class Repr(ABC):

    def __init__(self, context: "ReprContext") -> None:
        self.ctx = context 

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

    def __or__(self, other: "Repr") -> "Repr": return self.ctx.apply("|", self, other)
    def __and__(self, other: "Repr") -> "Repr": return self.ctx.apply("&", self, other)
    def __xor__(self, other: "Repr") -> "Repr": return self.ctx.apply("^", self, other)
    def __rshift__(self, other: "Repr") -> "Repr": return self.ctx.apply("->", self, other)
    def __lshift__(self, other: "Repr") -> "Repr": return self.ctx.apply("<-", self, other)
    def __invert__(self): return self.ctx.apply("~", self)
    def biimp(self, other: "Repr") -> "Repr": return self.ctx.apply("<->", self, other)

class ReprContext(ABC):
    @property
    @abstractmethod
    def false(self) -> "Repr": 
        raise NotImplementedError()

    @property
    @abstractmethod
    def true(self) -> "Repr": 
        raise NotImplementedError()

    @abstractmethod
    def apply(self, op: str, *children) -> "Repr":
        raise NotImplementedError() 

    @abstractmethod
    def var(self, x: str) -> "Repr": 
        raise NotImplementedError()

    def parse(self, formula: str) -> "Repr":
        def rec(parsed):
            op, args = parsed[0], parsed[1:]
            if op == "C" and args[0] == "0": return self.false
            elif op == "C" and args[0] == "1": return self.true
            elif op == "V": return self.var(args[0])
            else: return self.apply(op, *(rec(a) for a in args))
        return rec(parser.parse(formula))

import ast
from functools import cached_property, cache

# import re
# VARS_RE = re.compile(r"([a-zA-Z_][a-zA-Z_0-9]*)")

def tseytin(formula : "Formula", vars2idx=dict()):
    def subformulas(cur, counter, sequence):
        if isinstance(cur, str): # is a variable
            y = cur
            sequence.append((y,y))
            return y, counter
        op = cur[0]
        if op == "~":
            indicator, counter = subformulas(cur[1], counter, sequence)
            y = f"___tseytin_y{counter}"
            sequence.append( (y, ("~", indicator)) )
            return y, counter + 1
        
        left, counter = subformulas(cur[1], counter, sequence)
        right, counter = subformulas(cur[2], counter, sequence)
        y = f"___tseytin_y{counter}" 
        sequence.append((y, (left, op, right)))
        return y, counter + 1
    sequence = []
    ylast, _ = subformulas(formula.tree, 0, sequence)

    # print(sequence)
    # src: https://en.wikipedia.org/wiki/Tseytin_transformation
    vars = set(indicator for indicator,_ in sequence)
    vars = { v: idx+1 for idx,v in enumerate(vars)} | vars2idx
    cnf = [ [ vars[ylast] ] ]
    for indicator, rhs in sequence:
        C = vars[indicator]
        if isinstance(rhs, str):
            continue
        if isinstance(rhs, tuple) and len(rhs) == 2: # negation
            A = vars[rhs[1]]
            cnf += [[-C, -A], [C, A]]
        if isinstance(rhs, tuple) and len(rhs) == 3:
            A, op, B = vars[rhs[0]], rhs[1], vars[rhs[2]]
            if op == "^":
                cnf += [[-C, -A, -B], [-C, A, B], [C, -A, B], [C, A, -B]]
            elif op == "&":
                cnf += [[-A, -B, C], [A, -C], [B, -C]]
            elif op == "|":
                cnf += [[A, B, -C], [-A, C], [-B, C]]
            else:
                raise Exception(f"operation {op} unknown!")
    return cnf, vars

# todo: make a "Operable" superclass that captures operations for CNF and BDDs?
# i.e. so the user can easily use sharpSAT and Buddy without many complications...

class Formula:
    def __init__(self, tree : tuple):
        self.tree = tree

    @classmethod
    def parse(cls, formula : str) -> "Formula":
        def rec(parsed_formula):
            if isinstance(parsed_formula, ast.Constant): # do nothing
                return str(parsed_formula.value)
            elif isinstance(parsed_formula, ast.Module): # do nothing
                return rec(parsed_formula.body[0])
            elif isinstance(parsed_formula, ast.Expr): # do nothing
                return rec(parsed_formula.value)
            elif isinstance(parsed_formula, ast.Name): # is a variable
                return parsed_formula.id 
            elif isinstance(parsed_formula, ast.UnaryOp):
                assert type(parsed_formula.op) in { ast.Invert, ast.Not } # negation
                return ( "~", rec(parsed_formula.operand) )
            elif isinstance(parsed_formula, ast.BinOp): # binary op
                op2str = { 
                    ast.BitOr: "|",
                    ast.BitXor: "^",
                    ast.BitAnd: "&" } # maybe implement the remainder later on
                    # ast.LShift: "<-",
                    # ast.RShift: "->",
                    # ast.Sub: "-" }
                assert type(parsed_formula.op) in op2str, type(parsed_formula.op)
                indicator_left = rec(parsed_formula.left)
                indicator_right = rec(parsed_formula.right)
                op = op2str[type(parsed_formula.op)]
                return ( op, indicator_left, indicator_right )
            else:
                raise Exception(f"Node {parsed_formula} of unknown type!")
        return Formula(rec(ast.parse(formula)))

    @cache
    def __repr__(self):
        def rec(cur):
            # TODO: improve ranking between cofactors & remove brackets
            if isinstance(cur, str): return cur
            op = cur[0]
            if op == "~": 
                operand = cur[1]
                if isinstance(operand, str): return f"~{operand}"
                else: return f"~({rec(operand)})"
            left, right = cur[1], cur[2]
            return f"({rec(left)}) {op} ({rec(right)})"
        return rec(self.tree)

    def cofactor(self, var : str, val : bool) -> "Formula":
        def rec(cur):
            if isinstance(cur, str): # is a variable
                if cur == var and val: return "1"
                elif cur == var and not val: return "0"
                else: return cur
            op = cur[0]
            if op == "~":
                sub = rec(cur[1])
                if sub == "0": return "1"
                elif sub == "1": return "0"
                else: return ("~", sub)
            left, right = rec(cur[1]), rec(cur[2])
            if op == "&":
                if left == "1": return right
                if left == "0": return "0"
                if right == "1": return left
                if right == "0": return "0"
            elif op == "|":
                if left == "0": return right
                if left == "1": return "1"
                if right == "0": return left
                if right == "1": return "1"
            elif op == "^":
                if left == "1": return rec(("~", right))
                if left == "0": return right 
                if right == "1": return rec(("~", left))
                if right == "0": return left
            return (op, left, right) 
        return Formula(rec(self.tree))

    def __apply(self, op, *others):
        if op == "~": return Formula(("~", self.tree))
        elif op in ["|", "^", "&"]: return Formula((op, self.tree, others[0].tree))
        else: raise Exception(f"operation {op} unknown!")
         
    def __and__(self, other : "Formula") -> "Formula": return self.__apply("&", other)
    def __or__(self, other : "Formula") -> "Formula": return self.__apply("|", other)
    def __xor__(self, other : "Formula") -> "Formula": return self.__apply("^", other)
    def __invert__(self) -> "Formula": return self.__apply("~")

    @cached_property
    def vars(self) -> set[str]:
        def rec(cur):
            if isinstance(cur, str): return { cur }
            elif cur[0] == "~": return rec(cur[1])
            else: return rec(cur[1]) | rec(cur[2])
        return rec(self.tree)

    @cached_property
    def cnf(self) -> tuple[list[list[int]], dict[str, int]]:
        return tseytin(self)

    def flip(self, var):
        def rec(cur):
            if isinstance(cur, str):
                if cur == var: return ("~", cur)
                else: return cur
            op = cur[0]
            if op == "~":
                if cur[1] == var: return cur[1]
                else: return ("~", rec(cur[1]))
            left, right = rec(cur[1]), rec(cur[2])
            return (op, left, right)
        return Formula(rec(self.tree))
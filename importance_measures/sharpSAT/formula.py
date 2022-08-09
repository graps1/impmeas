import ast
from functools import cached_property, cache

# import re
# VARS_RE = re.compile(r"([a-zA-Z_][a-zA-Z_0-9]*)")

# doesn't seem that necessary
# class CNF:
#     def __init__(self, cnf : list[set]):
#         self.cnf = cnf
# 
#     def cofactor(self, var, val) -> "CNF":
#         if not val: return self.cofactor(-var, True)
#         ret = []
#         for clause in self.cnf:
#             if var in clause: continue
#             elif -var in clause: ret.append(clause - { -var })
#             else: ret.append(clause)
#         return CNF(ret)
#     
#     def flip(self, var) -> "CNF":
#         ret = []
#         for clause in self.cnf:
#             if var in clause: ret.append((clause - { var }) | { -var })
#             elif -var in clause: ret.append((clause - { -var }) | { var })
#             else: ret.append(clause)
#         return CNF(ret)


def tseytin(formula : "Formula", vars2idx=dict()) -> tuple[list[set], dict[str, int]]:
    def rec(cur, counter, dictionary):
        if isinstance(cur, str): # is a variable
            if cur not in dictionary: dictionary[cur] = cur
            return cur, counter
        op = cur[0]
        if op == "~":
            indicator, counter = rec(cur[1], counter, dictionary)
            val = ("~", indicator)
            if val not in dictionary:
                y = f"___tseytin_y{counter}" 
                dictionary[val] = y 
                counter += 1
            else: y = dictionary[val]
            return y, counter
        
        left, counter = rec(cur[1], counter, dictionary)
        right, counter = rec(cur[2], counter, dictionary)
        val = (op, left, right)
        if val not in dictionary: 
            y = f"___tseytin_y{counter}" 
            dictionary[val] = y
            counter += 1
        else: y = dictionary[val]
        return y, counter + 1
    dictionary = {} 
    ylast, _ = rec(formula.tree, 0, dictionary)

    # print(sequence)
    # src: https://en.wikipedia.org/wiki/Tseytin_transformation
    vars = set(indicator for _,indicator in dictionary.items())
    vars = { v: idx+1 for idx,v in enumerate(vars)} | vars2idx
    cnf = [ { vars[ylast] } ]
    for lhs, indicator in dictionary.items():
        C = vars[indicator]
        if isinstance(lhs, str):
            continue
        if isinstance(lhs, tuple) and len(lhs) == 2: # negation
            A = vars[lhs[1]]
            cnf += [{-C, -A}, {C, A}]
        if isinstance(lhs, tuple) and len(lhs) == 3:
            op, A, B = lhs[0], vars[lhs[1]], vars[lhs[2]]
            if op == "^":
                cnf += [{-C, -A, -B}, {-C, A, B}, {C, -A, B}, {C, A, -B}]
            elif op == "&":
                cnf += [{-A, -B, C}, {A, -C}, {B, -C}]
            elif op == "|":
                cnf += [{A, B, -C}, {-A, C}, {-B, C}]
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
                op = op2str[type(parsed_formula.op)]
                left = rec(parsed_formula.left)
                right = rec(parsed_formula.right)
                return ( op, left, right )
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
    def cnf(self) -> tuple[list[set], dict[str, int]]:
        return tseytin(self)

    def flip(self, var : str) -> "Formula":
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
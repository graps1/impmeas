from lark import Lark, Transformer

ASSOCIATIVE = [ "^", "&", "|" ]
OPERATIONS = ["~", "&", "|", "->", "<-", "^", "<->"] 
PRECEDENCE = {k:idx for idx,k in enumerate(["C", "V"] + OPERATIONS)}

grammar = '''
    start: _formula
    _formula: biimp_
            | xor_
            | limp_
            | rimp_
            | or_
            | and_
            | negation_
            | "(" _formula ")" 
            | variable 
            | constant 

    and_: _formula "&" _formula
    xor_: _formula "^" _formula
    or_: _formula "|" _formula
    biimp_: _formula "<->" _formula
    rimp_: _formula "->" _formula
    limp_: _formula "<-" _formula
    negation_: "~" _formula

    constant: CONSTANT 
    variable: CNAME 
    CONSTANT: "0" | "1"

    %import common.CNAME
    %ignore " "
'''

PARSER = Lark(grammar)

class FormulaTransformer(Transformer):
    
    def __init__(self):
        wrapper2ary = lambda val: (lambda items: (val, items[0], items[1]))    
        wrapper1ary = lambda val: (lambda items: (val, items[0]))    
        self.biimp_ = wrapper2ary("<->")
        self.or_ = wrapper2ary("|")
        self.and_ = wrapper2ary("&")
        self.limp_ = wrapper2ary("<-")
        self.rimp_ = wrapper2ary("->")
        self.xor_ = wrapper2ary("^")
        self.negation_ = wrapper1ary("~")

    def constant(self, items): return ("C", items[0].value)
    def variable(self, items): return ("V", items[0].value)
    def start(self, items): return items
    def formula(self, items): return items

def formula2tree(formula: str):
    tree = PARSER.parse(formula)
    result = FormulaTransformer().transform(tree)
    return result[0]
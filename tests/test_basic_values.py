from formulas import TableContext, FormulaContext, BuddyContext, GPMC
import impmeas as imp

TESTS = [
    ("x|y|z", "Bz/CCGM", 0.25, 0.25, 0.25),
    ("x&(~y)&z", "Bz/CCGM", 0.25, -0.25, 0.25),
    ("x&(~y)", "Bz/CCGM", 0.5, -0.5, 0),
    ("x^y^z", "Bz/CCGM", 0, 0, 0),
    ("x|(y^z)", "Bz/CCGM", 0.5, 0, 0),
    ("x|(y&z)", "Bz/CCGM", 0.75, 0.25, 0.25),

    ("x|y|z", "Sh/CCGM", 1/3, 1/3, 1/3),
    ("x&(~y)&z", "Sh/CCGM", 1/6, -1/3, 1/6),
    ("x&(~y)", "Sh/CCGM", 1/2, -1/2, 0),
    ("x^y^z", "Sh/CCGM", 1/3, 1/3, 1/3),
    ("x|(y^z)", "Sh/CCGM", 2/3, 1/6, 1/6),
    ("x|(y&z)", "Sh/CCGM", 2/3, 1/6, 1/6),

    ("x|y|z", "Blame", 0.4166666666, 0.4166666666, 0.4166666666),
    ("x&(~y)&z", "Blame", 0.4166666666, 0.4166666666, 0.4166666666),
    ("x&(~y)", "Blame", 0.625, 0.625, 0),
    ("x^y^z", "Blame", 1, 1, 1),
    ("x|(y^z)", "Blame", 0.625, 0.70833333333, 0.70833333333),
    ("x|(y&z)", "Blame", 0.8125, 0.4166666666, 0.4166666666),

    ("x|y|z", "I", 0.25, 0.25, 0.25),
    ("x&(~y)&z", "I", 0.25, 0.25, 0.25),
    ("x&(~y)", "I", 0.5, 0.5, 0),
    ("x^y^z", "I", 1, 1, 1),
    ("x|(y^z)", "I", 0.5, 0.5, 0.5),
    ("x|(y&z)", "I", 0.75, 0.25, 0.25),

    ("x|y|z", "Bz/DCGM", 0.25, 0.25, 0.25),
    ("x&(~y)&z", "Bz/DCGM", 0.25, 0.25, 0.25),
    ("x&(~y)", "Bz/DCGM", 0.5, 0.5, 0),
    ("x^y^z", "Bz/DCGM", 0.25, 0.25, 0.25),
    ("x|(y^z)", "Bz/DCGM", 0.75, 0.25, 0.25),
    ("x|(y&z)", "Bz/DCGM", 0.75, 0.25, 0.25),

    ("x|y|z", "Bz/RCGM", 0.25, 0.25, 0.25),
    ("x&(~y)&z", "Bz/RCGM", 0.25, 0.25, 0.25),
    ("x&(~y)", "Bz/RCGM", 0.5, 0.5, 0),
    ("x^y^z", "Bz/RCGM", 0.25, 0.25, 0.25),
    ("x|(y^z)", "Bz/RCGM", 0.25, 0.25, 0.25),
    ("x|(y&z)", "Bz/RCGM", 0.75, 0.25, 0.25),

    ("x|y|z", "Bz/QHCGM", 0.140625, 0.140625, 0.140625),
    ("x&(~y)&z", "Bz/QHCGM", 0.140625, 0.140625, 0.140625),
    ("x&(~y)", "Bz/QHCGM", 0.375, 0.375, 0),
    ("x^y^z", "Bz/QHCGM", 0.25, 0.25, 0.25),
    ("x|(y^z)", "Bz/QHCGM", 0.3125, 0.1875, 0.1875),
    ("x|(y&z)", "Bz/QHCGM", 0.640625, 0.140625, 0.140625)
]


def approx(v1, v2):
    return abs(v1 - v2) <= 1e-8

def test_values():
    contexts = {
        TableContext: TableContext(print_mode="primes"),
        BuddyContext: BuddyContext(["x", "y", "z"]),
        FormulaContext: FormulaContext(solver=GPMC())
    } 
    for formula, value_str, rx, ry, rz in TESTS:
        results = (rx, ry, rz)
        print(f"testing {formula} for {value_str}, expecting {rx:.4f} {ry:.4f} {rz:.4f} for x,y,z.")
        for method in imp.methods(value_str):
            print(f"  method = {method.__name__}")
            ctx = contexts[method]
            f = ctx.parse(formula)
            for x, r in zip("xyz", results):
                assert approx(imp.value(value_str, f, x), r), (type(ctx), f, value_str)
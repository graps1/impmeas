import impmeas as imp

TESTS = [
    ("x|y|z", imp.banzhaf, 0.25, 0.25, 0.25),
    ("x&(~y)&z", imp.banzhaf, 0.25, -0.25, 0.25),
    ("x&(~y)", imp.banzhaf, 0.5, -0.5, 0),
    ("x^y^z", imp.banzhaf, 0, 0, 0),
    ("x|(y^z)", imp.banzhaf, 0.5, 0, 0),
    ("x|(y&z)", imp.banzhaf, 0.75, 0.25, 0.25),

    ("x|y|z", imp.shapley, 1/3, 1/3, 1/3),
    ("x&(~y)&z", imp.shapley, 1/6, -1/3, 1/6),
    ("x&(~y)", imp.shapley, 1/2, -1/2, 0),
    ("x^y^z", imp.shapley, 1/3, 1/3, 1/3),
    ("x|(y^z)", imp.shapley, 2/3, 1/6, 1/6),
    ("x|(y&z)", imp.shapley, 2/3, 1/6, 1/6),

    ("x|y|z", imp.blame, 0.4166666666, 0.4166666666, 0.4166666666),
    ("x&(~y)&z", imp.blame, 0.4166666666, 0.4166666666, 0.4166666666),
    ("x&(~y)", imp.blame, 0.625, 0.625, 0),
    ("x^y^z", imp.blame, 1, 1, 1),
    ("x|(y^z)", imp.blame, 0.625, 0.70833333333, 0.70833333333),
    ("x|(y&z)", imp.blame, 0.8125, 0.4166666666, 0.4166666666),

    ("x|y|z", imp.influence, 0.25, 0.25, 0.25),
    ("x&(~y)&z", imp.influence, 0.25, 0.25, 0.25),
    ("x&(~y)", imp.influence, 0.5, 0.5, 0),
    ("x^y^z", imp.influence, 1, 1, 1),
    ("x|(y^z)", imp.influence, 0.5, 0.5, 0.5),
    ("x|(y&z)", imp.influence, 0.75, 0.25, 0.25),

    ("x|y|z", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.25, 0.25, 0.25),
    ("x&(~y)&z", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.25, 0.25, 0.25),
    ("x&(~y)", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.5, 0.5, 0),
    ("x^y^z", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.25, 0.25, 0.25),
    ("x|(y^z)", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.75, 0.25, 0.25),
    ("x|(y&z)", lambda f,x: imp.banzhaf(imp.dominating_cgm(f),x), 0.75, 0.25, 0.25),

    ("x|y|z", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.25, 0.25, 0.25),
    ("x&(~y)&z", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.25, 0.25, 0.25),
    ("x&(~y)", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.5, 0.5, 0),
    ("x^y^z", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.25, 0.25, 0.25),
    ("x|(y^z)", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.25, 0.25, 0.25),
    ("x|(y&z)", lambda f,x: imp.banzhaf(imp.rectifying_cgm(f),x), 0.75, 0.25, 0.25),

    ("x|y|z", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.140625, 0.140625, 0.140625),
    ("x&(~y)&z", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.140625, 0.140625, 0.140625),
    ("x&(~y)", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.375, 0.375, 0),
    ("x^y^z", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.25, 0.25, 0.25),
    ("x|(y^z)", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.3125, 0.1875, 0.1875),
    ("x|(y&z)", lambda f,x: imp.banzhaf(imp.hkr_cgm(f),x), 0.640625, 0.140625, 0.140625)
]


def approx(v1, v2):
    return abs(v1 - v2) <= 1e-8

def test_values():
        
    imp.formulas.set_pmc_solver()
    imp.formulas.set_buddy_context("x y z".split())

    classes = { imp.Table, imp.Formula, imp.BuddyNode }

    for formula, method, rx, ry, rz in TESTS:
        results = (rx, ry, rz)
        print(f"testing\n\t{formula}\n\tfor {method}\n\texpecting {rx:.4f} {ry:.4f} {rz:.4f} for x,y,z.")
        for cls in classes:
            print(f"\trepresentation class = {cls.__name__}")
            f = cls.parse(formula)
            for x, r in zip("xyz", results):
                assert approx(method(f, x), r), (type(f), f)
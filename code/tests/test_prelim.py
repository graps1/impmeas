import sys; sys.path.append("..")

from bidict import bidict
import binvec
import binfunc 
import cgm
import utils

TOLERANCE = 1e-10

def test_extension_length():
    '''
        checks whether

            |f| = |h| |f1| + |~h| |f0|

        holds, given that f is monotone modular in h w/ cofactors f1,f0 

        hash: G251iijzI4
    '''
    for _ in range(100):
        f,h,f1,f0 = utils.generate_module(4,3)
        assert len(f) == len(h)*len(f1) + len(~h)*len(f0)


def test_rel_extension_length():
    '''
        checks whether

            lambda(f) = lambda(h) lambda(f1) + (1-lambda(f1)) lambda(f0)

        holds, given that f is monotone modular in h w/ cofactors f1,f0

        hash: pyzC78dcsW
    '''
    for _ in range(100):
        f,h,f1,f0 = utils.generate_module(4,3)
        lamb = lambda l: len(l)/2**l.varcount
        l1 = lamb(f)
        l2 = lamb(h)*lamb(f1) + (1-lamb(h))*lamb(f0)
        assert abs(l1-l2) <= TOLERANCE

def test_type_propagation():
    '''
        checks if the type propagation lemma holds.

        hash: 0qIKqo6qVE
    '''

    # basic stuff: 
    # - h = c,
    # - h = x, x not in S,
    # - h = x, x in S
    pi, S = bidict({"x0": "y0", "x1": "y1"}), {"x1"}
    hs = [
        binfunc.from_lambda(lambda: 0),
        binfunc.from_lambda(lambda x0: x0),
        binfunc.from_lambda(lambda x1: x1)
    ]
    ths = [
        binfunc.from_lambda(lambda: 0),
        binfunc.from_lambda(lambda y0: y0),
        binfunc.from_lambda(lambda y1: ~y1)
    ]

    for h,th in zip(hs, ths):
        assert th == h.flip(S&h.vars).rename(pi) 

    # advanced stuff:
    # - h = g1 * g2,
    # - h = ~g1
    # - h = exists/forall T. g
    for _ in range(100):
        # negation
        g = binfunc.randfunc(4)
        pi, S = utils.random_equivalent(g.vars)
        assert ~(g.flip(S).rename(pi)) == (~g).flip(S).rename(pi)

        # composition of two functions
        g1, g2 = binfunc.randfunc(4), binfunc.randfunc(4)
        operations = [ "__and__", "__or__", "__xor__" ]
        for op in operations:
            h = getattr(g1, op)(g2)
            pi, S = utils.random_equivalent(h.vars)
            assert getattr(g1.flip(S).rename(pi), op)( g2.flip(S).rename(pi))  == h.flip(S).rename(pi)

        # quantification
        g = binfunc.randfunc(4)
        pi, S = utils.random_equivalent(g.vars)
        T = utils.random_subset(g.vars)
        assert g.exists(T).flip(S-T).rename(pi) == (g.flip(S).rename(pi)).exists({pi[x] for x in T})
        assert g.forall(T).flip(S-T).rename(pi) == (g.flip(S).rename(pi)).forall({pi[x] for x in T})


        


        

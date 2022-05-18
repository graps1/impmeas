import sys; sys.path.append("..")

import cgm 
import binvec
import binfunc
from utils import random_subset, random_monotone_function, random_equivalent, generate_module

vs = [ cgm.omega, cgm.nu ]

def test_monotonicity():
    '''
        checks whether the biased CGMs are monotone

        hash: sQ2uh27sJS
    '''
    for _ in range(100):
        f = binfunc.randfunc(bits=6, var_prefix="x")
        S = random_subset(f.vars)
        T = random_subset(S)
        for v in vs:
            assert v(S, f) >= v(T, f)


def test_equality_for_monotonic_functions():
    '''
        checks whether the biased CGMs agree for monotone boolean functions

        hash: 8hzE6SxRKD
    '''
    for _ in range(100):
        F = { f"x{idx}" for idx in range(5) }
        f = random_monotone_function(F)
        for S in binvec.itersets(f.vars):
            assert cgm.characteristic(S, f) == cgm.omega(S, f) == cgm.nu(S, f)


def test_quantifier_swap_for_monotone_extensions():
    '''
        checks whether 

            Exists G. Forall T. f =  Forall T. Exists G. f 

        assuming f is monotonically modular in g, T subset F - G

        hash: AW0bTa1qHX
    '''
    for _ in range(100):
        f,g,_,_ = generate_module(4,3,monotone=True)
        T = random_subset(f.vars-g.vars)
        assert cgm.exists(g.vars, cgm.forall(T, f)) == \
               cgm.forall(T, cgm.exists(g.vars, f))


def test_decomposition():
    '''
        checks whether 

            v_f = (v_g & v_f1) | v_f0

        holds, given F cup (G cap H) = emptyset and g >= h

        hash: smuV9vBwJ8 
    '''
    for _ in range(100):
        f,g,f1,f0 = generate_module(4,3,monotone=True)
        S = random_subset(f.vars)
        for v in vs:
            assert v(S,f) == (v(S,g) and v(S,f1)) or v(S,f0)

def test_difference():
    '''
        checks whether 

            v(S|{x},f) - v(S,f) = 1 iff 
            v(S|{x},g) - v(S,g) = 1 AND v(S,f1) = 1 AND v(S,f0) = 0

        holds, given F cup (G cap H) = emptyset and g >= h

        hash: kBvOloehVe
    '''
    for _ in range(100):
        f,g,f1,f0 = generate_module(4,3,monotone=True)
        S = random_subset(f.vars)
        for v in vs:
            diff_f = v(S|{"x0"},f) - v(S,f)
            diff_g = v(S|{"x0"},g) - v(S,g)
            assert diff_f == (diff_g and v(S,f1) and not v(S,f0))


def test_type_invariance():
    '''
        checks whether

            v(T, h) = v(pi(T), g)
    
        holds for all T, assuming that g is the (pi, S)-equivalent of h

        hash: hY1Wmc2eBg
    '''
    for _ in range(100):
        h = binfunc.randfunc(bits=6, var_prefix="x")
        pi, S = random_equivalent(h.vars, var_pref="y")
        g = h.flip(S).rename(pi)
        for v in vs:
            for T in binvec.itersets(h.vars):
                piT = { pi[x] for x in T }
                assert v(T, h) == v(piT, g)

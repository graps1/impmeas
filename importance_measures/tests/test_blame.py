import sys; sys.path.append("..")

import blame
import binfunc
import binvec 

from bidict import bidict

from utils import random_equivalent, generate_SRC_parameters, generate_module

TOLERANCE = 1e-10

rhos = [
    lambda x: 1/(x+1),
    lambda x: 2**(-x),
    lambda x: 1 if x == 0 else 0
]

def test_blame_type_and_compl_invariance():
    '''
        checks whether the type- and complement-invariance property of the blame holds

        hash: gaopsnx0Gd
    '''
    for _ in range(100):
        f = binfunc.randfunc(bits=4, var_prefix="x")
        pi, S = random_equivalent(f.vars, var_pref="y")
        h = f.flip(S).rename(pi)
        # there might be some rounding errors, so check if the values are "close enough"
        for rho in rhos:
            diff1 = blame.blame("x0", f, rho=rho) - blame.blame(pi["x0"], h, rho=rho)
            diff2 = blame.blame("x0", f, rho=rho) - blame.blame("x0", ~f, rho=rho)
            assert abs(diff1) <= TOLERANCE
            assert abs(diff2) <= TOLERANCE


def test_blame_nonincreasing_importance():
    '''
        checks whether the importance of a variable decreases if a function is 
        extended monotonically

        hash: U7jbpmrlnt
    '''
    for _ in range(100):
        f,h,_,_ = generate_module(3,2,monotone=True)
        for rho in rhos:
            b1 = blame.blame("x0", h, rho)
            b2 = blame.blame("x0", f, rho)
            assert b1 >= b2 - TOLERANCE


def test_blame_equiv_vars():
    '''
        checks whether the blame fulfills property SRC^S 
        property

        hash: Scjxa9Mk6I
    '''
    for _ in range(10):
        f,_,_,_,_,x,y = generate_SRC_parameters(2,3,strong=True)
        for rho in rhos:
            b1 = blame.blame(x, f, rho=rho)
            b2 = blame.blame(y, f, rho=rho)
            assert b2 >= b1 - TOLERANCE


def test_influence_NIM_MRP():
    '''
        checks whether the Influence can be decomposed as 

            - Inf_x(f) = |f1^f0|/2^(|F|-|H|) * Inf_x(h)
        
        and whether it fulfills

            - Inf_x(f) <= Inf_x(h)
            - Inf_x(h) >= Inf_y(h) implies Inf_x(f) >= Inf_y(f)

        whenever f is modular in h.

        hash: wqIvk7atKj
    '''
    rho = lambda x: 1 if x == 0 else 0
    for _ in range(100):
        f,g,f1,f0 = generate_module(3,3,monotone=False)
        x, y = "x0", "x1"
        bfx = blame.blame(x, f, rho=rho)
        bgx = blame.blame(x, g, rho=rho)
        coeff = len(f1^f0)/2**len(f.vars - g.vars)
        assert abs( coeff*bgx - bfx) <= TOLERANCE
        assert bgx >= bfx - TOLERANCE

        bfy = blame.blame(y, f, rho=rho)
        bgy = blame.blame(y, g, rho=rho)
        if bgy > bgx:
            assert bfy >= bfx - TOLERANCE
        else:
            assert bfx >= bfy - TOLERANCE

        
            



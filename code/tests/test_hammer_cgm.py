import sys; sys.path.append("..")

import binvec
import binfunc
import cgm
from utils import random_equivalent, random_subset, c, C, generate_module
from math import log2

TOLERANCE = 1e-10

quadratic_rho = lambda x: 4*(x-0.5)**2 

rhos = [
    quadratic_rho,
    lambda x: 1 if x in [0,1] else 1+x*log2(x)+(1-x)*log2(1-x),
    lambda x: 2*abs(x-0.5)
]

def test_type_invariance():
    '''
        checks whether 
            
            E_{h,rho}(T) = E_{g,rho}(pi(T))

        holds, given that g is the (pi,S)-equivalent of h

        hash: o2hc3O6a4Q 
    '''
    for _ in range(100):
        h = binfunc.randfunc(bits=6, var_prefix="x")
        pi, S = random_equivalent(h.vars, var_pref="y")
        g = h.flip(S).rename(pi)
        T = random_subset(h.vars)
        piT = { pi[x] for x in T }
        for rho in rhos:
            assert abs(cgm.hammer(T, h, rho=rho) - cgm.hammer(piT, g, rho=rho)) <= TOLERANCE


def test_compl_invariance():
    '''
        checks whether

            E_{f,rho}(S) = E_{~f,rho}(S)

        holds.

        hash: LRa5B1wrsE
    '''
    for _ in range(100):
        f = binfunc.randfunc(bits=6, var_prefix="x")
        S = random_subset(f.vars)
        nf = ~f
        for rho in rhos:
            assert abs(cgm.hammer(S, f, rho=rho) - cgm.hammer(S, nf, rho=rho)) <= TOLERANCE



def test_decomposition():
    '''
        suppose f is modular in h with cofactors s (positive) and t (negative)
        checks whether the mapping rho : x -> 4*(x-0.5)**2 w/ E_{f,rho} = E_f fulfills

            E_f(B|A|{x}) - E_f(B|A) = c(B,s,t)*(E_h(A|{x}) - E_A(B))
            
            with c(B,s,t) = (1/2**|B|)(sum_{beta in B(B)} ( lambda(s_beta) - lambda(t_beta) )**2

        for B subset F-H, A subset H.

        hash: cbcn0O7JCU
    '''
    for _ in range(100):
        f,h,s,t = generate_module(4,3)
        A = random_subset(h.vars)
        B = random_subset(f.vars - h.vars)
        
        diff1 = cgm.d(cgm.hammer, A|B, "x0", f)
        diff2 = c(B,s,t)*cgm.d(cgm.hammer, A, "x0", h)

        assert abs( diff1 - diff2 ) <= TOLERANCE 

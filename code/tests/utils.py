import sys; sys.path.append("..")
from typing import Set, Tuple

import binvec
import binfunc

from random import randint, shuffle, choices
from bidict import bidict

def random_vector(F : Set[str]) -> binvec.vec:
    '''
        generates a random binvec.binvec instance with variables in F
    '''
    return binvec.vec({ x: randint(0,1) for x in F })

def random_subset(F: Set[str]) -> Set[str]:
    '''
        returns a random subset of F
    '''
    return set(list(F)[:randint(0, len(F))])

def random_equivalent(F : Set[str], var_pref = "y") -> Tuple[bidict[str,str], Set[str]]:
    '''
        generates a random renaming pi : F -> H and a random subset of F
        where H = [ 'y0', 'y2', ... ] depends on the given variable prefix. 
    '''
    H = [f"{var_pref}{idx}" for idx in range(len(F))]
    F = list(F)
    shuffle(H), shuffle(F)
    pi = bidict({ x: y for x, y in zip(F, H)})
    S = random_subset(F) 
    return pi, S

def random_monotone_function(F : Set[str]) -> binfunc.func: 
    '''
        generates random monotone boolean functions according to the given set of variables
    '''
    f = binfunc.init_empty(F)
    for _ in range( randint(0,2**len(F)) ):
        u = random_vector(F)
        S = { x for x in u.vars if u[x] == 1 }
        u = u.restrict(S)
        for uext in binvec.itervecs(F - S):
            f[u // uext] = 1
    return f

def generate_module(modulevars=2, cofactorvars=3, monotone=False):
    '''
        returns a tuple (f,g,f1,f0) where
            - f is modular in g
            - g is the module
            - f1 is the positive and f0 the negative cofactor of f wrt g
        if `monotone` is set to true, then f is monotone in g
    '''
    f1 = binfunc.randfunc(cofactorvars, var_prefix="z")
    f0 = binfunc.randfunc(cofactorvars, var_prefix="z")
    if monotone:
        f1 = f1 | f0
    g = binfunc.randfunc(modulevars, var_prefix="x")
    f = g&f1 | ~g&f0
    return f,g,f1,f0

def generate_SRC_parameters(modulevars=2, cofactorvars=3, strong=True):
    '''
        generates a tuple (f,h,g,pi,S,x,y) such that 
            - f is (monotone) modular in h and g = pi(h^S)
            - g is a substitute for h in f
            - x is a variable in h
            - y = pi(x) is a variable in g
    '''
    h = None
    while h is None or len(h) == 0 or len(h) == 2**modulevars:
        # generate a non-constant module
        h = binfunc.randfunc(modulevars, var_prefix="x")
    pi, S = random_equivalent(h.vars, var_pref="y")
    g = h.flip(S).rename(pi)
    f11, f01, f10, f00 = binfunc.rand_substitute(cofactorvars, varpref="z", monotone=not strong)
    f = h&g&f11 | h&~g&f10 | ~h&g&f01 | ~h&~g&f00
    x, y = "x0", pi["x0"]
    return f, h, g, pi, S, x, y

def get_cofactor(g, f, c):
    '''
        returns the cofactor f_{g/c}
    '''
    w = None
    for u in binvec.itervecs(g.vars):
        if g[u] == c:
            w = u
            break
    assert w is not None
    return f.cofactor(w)


def c(K : Set[str], s : binfunc.func, t : binfunc.func) -> float:
    '''
        computes the coefficient known from the quadratic hammer-mapping
    '''
    lamb = lambda l: len(l)/2**l.varcount
    ret = 0
    for beta in binvec.itervecs(K):
        diff = lamb(s.cofactor(beta)) - lamb(t.cofactor(beta))
        ret += diff**2
    return ret/2**len(K)

def C(s : binfunc.func, t : binfunc.func) -> float:
    ret = 0
    for K in binvec.itersets(s.vars | t.vars):
        ret += c(K,s,t)
    return ret/2**(len(s.vars|t.vars))
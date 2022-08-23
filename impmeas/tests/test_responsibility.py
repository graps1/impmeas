import sys; sys.path.append("..")

import blame
import binfunc
import binvec

from utils import random_equivalent, random_vector, generate_module, generate_SRC_parameters
from random import randint


def test_resp_type_invariance():
    '''
        checks whether the type-invariance-lemma of the responsibility holds.

        hash: xVUAbTr5T4 
    '''
    for _ in range(100):
        f = binfunc.randfunc(bits=4, var_prefix="x")
        # create (pi,S)-equivalent function
        pi, S = random_equivalent(f.vars)
        h = f.flip(S).rename(pi)
        
        # create a random vector
        u = random_vector(f.vars)
        uprime = (u^binvec.incidence(S, f.vars)).rename(pi)
        c = randint(0,1)

        assert blame.r("x0", u, f, c) == blame.r(pi["x0"], uprime, h, c)


def test_resp_compl_invariance():
    '''
        checks whether the complementation-invariance-lemma of the responsibility holds.
        - r^u_x(f,c) = r^u_x(~f,~c)
        - r^u_x(f,c) = r^{u + 1_x}_x(f,~c)

        hash: YHsuCLGUpC 
    '''
    for _ in range(100):
        f = binfunc.randfunc(bits=4, var_prefix="x")
        u = random_vector(f.vars)
        c = randint(0, 1)
        assert blame.r("x0", u, f, c) == blame.r("x0", u, ~f, not c)
        
        uprime = u^binvec.incidence({"x0"}, f.vars)
        assert blame.r("x0", u, f, c) == blame.r("x0", uprime, f, not c)


# def test_distance_properties():
#     '''
#         checks whether the following properties hold:
#         - k^u(f & g) >= k^u(f)
#         - k^u(f | g) = min { k^u(f), k^u(g) } 
#         - k^u(f & g) = k^u(f) + k^u(g)      if F cap G = emptyset
#         - k^w(f) = k^v(h)
# 
#         where u is a vector over F cup G, w is a vector over F, 
#         h is a (pi, S)-equivalent of f and v the (pi, S)-equivalent of w
#         (we take w = u_F for simplicity, but that does not make a difference.)
#     '''
# 
#     for _ in range(100):
#         f = binfunc.randfunc(bits=4, var_prefix="x").reduce_to_core()
#         g = binfunc.randfunc(4, var_prefix="x", name="g").reduce_to_core()
#         # function with disjunct variables
#         l = binfunc.randfunc(4, var_prefix="y", name="l").reduce_to_core() 
#         
#         u_FG = random_vector(f.vars | g.vars)
#         u_L = random_vector(l.vars)
#         
#         # (pi,S)-equivalents h and v
#         pi, S = random_equivalent(f.vars, var_pref="z")
#         h = f.flip(S).rename(pi)
#         v = (u_FG.restrict(f.vars)^binvec.incidence(S, f.vars)).rename(pi)
# 
#         ku_f = blame.k(u_FG, f)
#         ku_g = blame.k(u_FG, g)
#         ku_l = blame.k(u_L, l)
# 
#         assert blame.k(u_FG, f&g) >= ku_f
#         assert blame.k(u_FG, f|g) == min( ku_f, ku_g )
#         assert blame.k(u_FG // u_L, f&l) == ku_f + ku_l
#         assert ku_f == blame.k(v, h)


def test_resp_decomposition():
    '''
        checks whether the decomposition-lemma of the responsibility holds:
            
            r^u_x( f , c) = r^u_x(g,c) + k^u(~f0 & f1)

        where f is monotone modular in g

        hash: Ps5Ba3pl1l
    '''
    for _ in range(100):
        f,g,f1,f0 = generate_module(4,3,monotone=True)
        c = randint(0,1)
        u = random_vector(f.vars) 
        u_G, u_FmG = u.restrict(g.vars), u.restrict(f.vars - g.vars)
        assert blame.r("x0", u, f, c) == blame.r("x0", u_G, g, c) + blame.k(u_FmG, ~f0 & f1)


def test_resp_rank_equiv_vars():
    '''
        checks a few lemmas that are used for showing that the 
        "ranking between equivalent variables"-property holds for the blame:

        - f(u) != f(u + 1_x) implies f(hat u) != f(hat u + 1_y)
        - r^u_x(f, c) >= r^{hat u}_y(f, c)
        - rho(r^{hat u}_y(f)) + rho(r^{hat u + 1_y}_y(f)) >= rho(r^u_x(f)) + rho(r^{u + 1_x}_x(f))
        
        where  
            - f is modular in g, h such that g is a substitute for h in f
            - g = pi(h^S)
            - x a variable in H,
            - y = pi(x) a variable in G
            - u -> hat u is the switching function, 

        ** the third inequality is not tested directly, but check a case that implies the inequality
        using the fact that rho is monotonically decreasing

        hash: BBU8Ybfk3i
    '''
    for _ in range(50):
        f,_,_,pi,S,x,y = generate_SRC_parameters(2,3,strong=True)

        u = random_vector(f.vars)
        u_1x = u^binvec.incidence(x, f.vars)
        uprime = u.apply_switch(pi, S)
        uprime_1y = uprime^binvec.incidence(y, f.vars)
        c = randint(0,1)

        assert f[u] == f[u_1x] or f[uprime] != f[uprime_1y]
        assert blame.r(x, u, f, c) >= blame.r(y, uprime, f, c)
        assert (blame.r(x, u, f) >= blame.r(y, uprime, f) and \
                blame.r(x, u_1x, f) >= blame.r(y, uprime_1y, f)) or \
               (blame.r(x, u_1x, f) >= blame.r(y, uprime, f)  and \
                blame.r(x, u, f) >= blame.r(y, uprime_1y, f))


        





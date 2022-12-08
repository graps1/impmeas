import impmeas as imp
from utils import X,Y
from random import randint


def test_resp_type_invariance():
    '''
        checks whether the type-invariance-lemma of the responsibility holds.

        hash: xVUAbTr5T4 
    '''
    for _ in range(100):
        Xss, Yss = X[:4], Y[:4]
        f = imp.random_table(Xss)
        pi = {x:y for x,y in zip(Xss,Yss)}
        S = imp.random_subset(Xss)
        h = f.flip(S).replace(pi)
        
        # create a random vector
        u = imp.random_assignment(f.vars)
        uprime = u | { y: not u[y] for y in S }
        uprime = { pi[y]: uprime[y] for y in f.vars }
        c = randint(0,1)

        assert imp.scs( f, "x0", u, c) == imp.scs(h, pi["x0"], uprime, c)


def test_resp_compl_invariance():
    '''
        checks whether the complementation-invariance-lemma of the responsibility holds.
        - scs^u_x(f,c) = scs^u_x(~f,~c)
        - scs^u_x(f,c) = scs^{u + 1_x}_x(f,~c)

        hash: YHsuCLGUpC 
    '''
    for _ in range(100):
        f = imp.random_table(X[:4])
        u = imp.random_assignment(f.vars)
        c = randint(0, 1)
        assert imp.scs( f, "x0", u, c) == imp.scs( ~f, "x0", u, not c)
        
        uprime = u | { "x0": not u["x0"] }
        assert imp.scs( f, "x0", u, c) == imp.scs( f, "x0", uprime, not c)


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
            
            scs^u_x( f , c) = scs^u_x(g,c) + d^u(~f0 & f1)

        where f is monotone modular in g

        hash: Ps5Ba3pl1l
    '''
    for _ in range(100):
        f,g,f1,f0 = imp.random_module(X[:4], Y[:3], monotone=True)
        c = randint(0,1)
        u = imp.random_assignment(f.vars) 
        assert imp.scs(f, "x0", u, c) == imp.scs( g, "x0", u, c) + imp.d(~f0 & f1, u)

def test_alt_resp_decomposition():
    '''
        checks whether the decomposition-lemma of the responsibility holds:
            
            mscs^u_x( f ) = mscs^u_x(g) + mscs^u_g(f )

        where f is modular in g
    '''
    for _ in range(100):
        f,g,f1,f0 = imp.random_module(X[:4], Y[:3])
        f_template = imp.Table.var("z").ite(f1, f0)
        u = imp.random_assignment(f.vars) 
        assert imp.mscs(f, "x0", u) == imp.mscs( g, "x0", u) + imp.mscs( f_template, "z", u)

def test_resp_rank_SUD():
    '''
        checks a few lemmas that are used for showing that the 
        "ranking between equivalent variables"-property holds for the blame:

        - rho(scs^{u}_x(f)) + rho(scs^{u + 1_x}_x(f)) >= rho(scs^u_x(h)) + rho(scs^{u + 1_x}_x(h))
        
        where  
            - f, h monotone modular in g,
            - f_{g/1} >= h_{g/1} and f_{g/0} <= h_{g/0}
            - x a variable in dep(g),
    '''
    for _ in range(50):
        Xss, Yss = X[:3], Y[:3]
        g = imp.random_table(Xss) 
        f0 = imp.random_table(Yss) 
        h0 = imp.random_table(Yss) | f0  # h0 >= f0
        h1 = imp.random_table(Yss) | h0  # h1 >= h0 <= f1
        f1 = imp.random_table(Yss) | h1  # f1 >= h1
        h = g.ite(h1,h0)
        f = g.ite(f1,f0)

        x = "x0"
        u = imp.random_assignment(f.vars)
        u_1x = u | { x: not u[x]}

        assert (imp.scs(f,x,u) <= imp.scs(h,x,u) and \
                imp.scs(f,x,u_1x) <= imp.scs(h,x,u_1x)) or \
               (imp.scs(f,x,u_1x) <= imp.scs(h,x,u)  and \
                imp.scs(f,x,u) <= imp.scs(h,x,u_1x))

# def test_resp_rank_equiv_vars():
#     '''
#         checks a few lemmas that are used for showing that the 
#         "ranking between equivalent variables"-property holds for the blame:
# 
#         - f(u) != f(u + 1_x) implies f(hat u) != f(hat u + 1_y)
#         - r^u_x(f, c) >= r^{hat u}_y(f, c)
#         - rho(r^{hat u}_y(f)) + rho(r^{hat u + 1_y}_y(f)) >= rho(r^u_x(f)) + rho(r^{u + 1_x}_x(f))
#         
#         where  
#             - f is modular in g, h such that g is a substitute for h in f
#             - g = pi(h^S)
#             - x a variable in H,
#             - y = pi(x) a variable in G
#             - u -> hat u is the switching function, 
# 
#         ** the third inequality is not tested directly, but check a case that implies the inequality
#         using the fact that rho is monotonically decreasing
# 
#         hash: BBU8Ybfk3i
#     '''
#     for _ in range(50):
#         f,_,_,pi,S,x,y = generate_SRC_parameters(2,3,strong=True)
# 
#         u = random_vector(f.vars)
#         u_1x = u^binvec.incidence(x, f.vars)
#         uprime = u.apply_switch(pi, S)
#         uprime_1y = uprime^binvec.incidence(y, f.vars)
#         c = randint(0,1)
# 
#         assert f[u] == f[u_1x] or f[uprime] != f[uprime_1y]
#         assert blame.r(x, u, f, c) >= blame.r(y, uprime, f, c)
#         assert (blame.r(x, u, f) >= blame.r(y, uprime, f) and \
#                 blame.r(x, u_1x, f) >= blame.r(y, uprime_1y, f)) or \
#                (blame.r(x, u_1x, f) >= blame.r(y, uprime, f)  and \
#                 blame.r(x, u, f) >= blame.r(y, uprime_1y, f))


        





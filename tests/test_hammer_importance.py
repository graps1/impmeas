import impmeas as imp
from utils import X,Y

TOLERANCE = 1e-10

def test_bz_decomposition():
    '''
        checks whether the decomposition 

            - Bz_x(E_f) = Bz_g(E_f) * Bz_x(E_h)

        holds true if kappa is chosen to be quadratic, 
        f is modular in h

        hash: QP8JusiwTC 
    '''
    for _ in range(50):
        f,h,f1,f0 = imp.random_module(X[:4], Y[:3])
        f_template = imp.Table.var("z").ite(f1,f0)
        bz1 = imp.banzhaf(imp.hkr_cgm(f), "x0")
        bz2 = imp.banzhaf(imp.hkr_cgm(h), "x0")
        bz3 = imp.banzhaf(imp.hkr_cgm(f_template), "z")
        assert abs( bz1 - bz2*bz3 ) <= TOLERANCE 

def test_SUD():
    '''
        check that 

            Bz_x(E_f) >= Bz_x(E_h)

        where 
            - f, h is monotonically modular in g,
            - f_{g/1} >= h_{g/1} and f_{g/0} <= h_{g/0}
            - x in dep(g)
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
        assert imp.banzhaf(imp.hkr_cgm(f), "x0") >= imp.banzhaf(imp.hkr_cgm(h), "x0") - TOLERANCE

# def test_SRC_weak_lemmas():
#     '''
#         check if we have the inequalities
# 
#             ( lambda((f_{g/1})_{alpha; beta}) - lambda((f_{g/0})_{alpha;beta}) )^2 >=
#             ( lambda((f_{h/1})_{alpha; tilde beta}) - lambda((f_{h/0})_{alpha; tilde beta}) )^2
#         
#         for all alpha in B(A), beta in B(B), tilde beta = pi(beta + 1_S),
#         and
# 
#             c(A|B, f_{g/1}, f_{g/0}) >= c(A|pi(B), f_{h/1}, f_{h/0})
# 
#         for all A ss F-(G|H), B ss H, 
# 
#         whenever f is monotone modular in g and h w/
#             - g = pi(h^S) for a VP (pi,S)
#             - g is a substitute for h in f
#             - x is a variable in g
#             - y = pi(x) is a variable in h
# 
#         hash: ODwRBJiuTT
#     '''
#     for _ in range(100):
#         f,h,g,pi,S,_,_ = utils.generate_SRC_parameters(2, 3, strong=False)
#         A = utils.random_subset(f.vars - (h.vars|g.vars))
#         B = utils.random_subset(h.vars)
#         alpha = utils.random_vector(A)
#         beta = utils.random_vector(B)
#         tbeta = (beta^binvec.incidence(S&B,B)).rename(pi)
#         fg1, fg0 = utils.get_cofactor(g, f, 1), utils.get_cofactor(g, f, 0)
#         fh1, fh0 = utils.get_cofactor(h, f, 1), utils.get_cofactor(h, f, 0) 
#         lamb = lambda l: len(l)/2**l.varcount
# 
#         # first inequality 
#         diff_left = ( lamb(fg1.cofactor(alpha // beta)) - lamb(fg0.cofactor(alpha // beta )) )**2
#         diff_right = ( lamb(fh1.cofactor(alpha // tbeta)) - lamb(fh0.cofactor(alpha // tbeta )) )**2
#         assert diff_left >= diff_right
# 
#         # second inequality
#         assert utils.c(A|B, fg1, fg0) >= utils.c(A|{pi[z] for z in B}, fh1, fh0)


# def test_SRC_weak_thr():
#     '''
#         check that 
# 
#             Bz_y(E_f) >= Bz_x(E_f)
# 
#         whenever f is monotone modular in g and h w/
#             - g = pi(h^S) for a VP (pi,S)
#             - g is a substitute for h in f
#             - x is a variable in g
#             - y = pi(x) is a variable in h
# 
#         hash: 6Jd8a8EJgl 
#     '''
#     for _ in range(50):
#         f,_,_,_,_,x,y = utils.generate_SRC_parameters(2, 3, strong=False)
#         bz = lambda x, l: cgm.banzhaf(cgm.hammer, x, l)
#         assert bz(y, f) >= bz(x, f) - TOLERANCE
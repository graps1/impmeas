import sys; sys.path.append("..")

import binvec
import binfunc 
import cgm
import utils

TOLERANCE = 1e-10

def test_bz_decomposition():
    '''
        checks whether the decomposition 

            - Bz_x(E_f) = C(f1,f0) Bz_x(E_h)

        holds true if rho is choosen to be quadratic, 
        f is modular in h w/ cofactors f1,f0

        hash: QP8JusiwTC 
    '''
    for _ in range(100):
        f,h,f1,f0 = utils.generate_module(4,3)
        bz1 = cgm.banzhaf(cgm.hammer, "x0", f)        
        bz2 = utils.C(f1,f0)*cgm.banzhaf(cgm.hammer, "x0", h)
        assert abs( bz1 - bz2 ) <= TOLERANCE 

def test_SRC_weak_lemmas():
    '''
        check if we have the inequalities

            ( lambda((f_{g/1})_{alpha; beta}) - lambda((f_{g/0})_{alpha;beta}) )^2 >=
            ( lambda((f_{h/1})_{alpha; tilde beta}) - lambda((f_{h/0})_{alpha; tilde beta}) )^2
        
        for all alpha in B(A), beta in B(B), tilde beta = pi(beta + 1_S),
        and

            c(A|B, f_{g/1}, f_{g/0}) >= c(A|pi(B), f_{h/1}, f_{h/0})

        for all A ss F-(G|H), B ss H, 

        whenever f is monotone modular in g and h w/
            - g = pi(h^S) for a VP (pi,S)
            - g is a substitute for h in f
            - x is a variable in g
            - y = pi(x) is a variable in h

        hash: ODwRBJiuTT
    '''
    for _ in range(100):
        f,h,g,pi,S,_,_ = utils.generate_SRC_parameters(2, 3, strong=False)
        A = utils.random_subset(f.vars - (h.vars|g.vars))
        B = utils.random_subset(h.vars)
        alpha = utils.random_vector(A)
        beta = utils.random_vector(B)
        tbeta = (beta^binvec.incidence(S&B,B)).rename(pi)
        fg1, fg0 = utils.get_cofactor(g, f, 1), utils.get_cofactor(g, f, 0)
        fh1, fh0 = utils.get_cofactor(h, f, 1), utils.get_cofactor(h, f, 0) 
        lamb = lambda l: len(l)/2**l.varcount

        # first inequality 
        diff_left = ( lamb(fg1.cofactor(alpha // beta)) - lamb(fg0.cofactor(alpha // beta )) )**2
        diff_right = ( lamb(fh1.cofactor(alpha // tbeta)) - lamb(fh0.cofactor(alpha // tbeta )) )**2
        assert diff_left >= diff_right

        # second inequality
        assert utils.c(A|B, fg1, fg0) >= utils.c(A|{pi[z] for z in B}, fh1, fh0)
        


def test_SRC_weak_thr():
    '''
        check that 

            Bz_y(E_f) >= Bz_x(E_f)

        whenever f is monotone modular in g and h w/
            - g = pi(h^S) for a VP (pi,S)
            - g is a substitute for h in f
            - x is a variable in g
            - y = pi(x) is a variable in h

        hash: 6Jd8a8EJgl 
    '''
    for _ in range(50):
        f,_,_,_,_,x,y = utils.generate_SRC_parameters(2, 3, strong=False)
        bz = lambda x, l: cgm.banzhaf(cgm.hammer, x, l)
        assert bz(y, f) >= bz(x, f) - TOLERANCE
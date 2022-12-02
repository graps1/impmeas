import impmeas as imp
from utils import X,Y
from math import log2

TOLERANCE = 1e-10

kappa_quad = lambda x: 4*(x-0.5)**2 

kappas = [
    kappa_quad,
    lambda x: 1 if x in [0,1] else 1+x*log2(x)+(1-x)*log2(1-x),
    lambda x: 2*abs(x-0.5)
]

def test_type_invariance():
    '''
        checks whether 
            
            E_h^kappa(T) = E_h^kappa(pi(T))

        holds, given that h = pi(h ^ S)

        hash: o2hc3O6a4Q 
    '''
    for _ in range(100):
        Xss,Yss = X[:4],Y[:4]
        f = imp.random_table(Xss)
        pi = { x:y for x,y in zip(Xss,Yss)}
        S = imp.random_subset(Xss)
        h = f.flip(S).replace(pi)
        T = imp.random_assignment(Xss)
        piT = { pi[x]: T[x] for x in T }
        for kappa in kappas:
            hkr_f = imp.hkr_cgm(f, kappa=kappa)
            hkr_h = imp.hkr_cgm(h, kappa=kappa)
            assert abs(hkr_f[T] - hkr_h[piT]) <= TOLERANCE


def test_compl_invariance():
    '''
        checks whether

            E_{f}^kappa(S) = E_{~f}^kappa(S)

        holds.

        hash: LRa5B1wrsE
    '''
    for _ in range(100):
        f = imp.random_table(X[:6])
        S = imp.random_assignment(f.vars)
        nf = ~f
        for kappa in kappas:
            hkr_f = imp.hkr_cgm(f, kappa=kappa)
            hkr_nf = imp.hkr_cgm(nf, kappa=kappa)
            assert abs(hkr_f[S] - hkr_nf[S]) <= TOLERANCE



def test_decomposition():
    '''
        suppose f is modular in h with cofactors s (positive) and t (negative)
        checks whether the mapping rho : x -> 4*(x-0.5)**2 w/ E_{f}^kappa = E_f fulfills

            Dx E_f = (Dx E_g) * (Dg E_f)

        hash: cbcn0O7JCU
    '''
    for _ in range(10):
        f,g,s,t = imp.random_module(X[:3], Y[:3])
        f_template = imp.Table.var("z").ite(s,t)

        E_f = imp.hkr_cgm(f, kappa=kappa_quad) 
        E_g = imp.hkr_cgm(g, kappa=kappa_quad)
        E_f_template = imp.hkr_cgm(f_template, kappa=kappa_quad)

        for S in imp.iter_assignments(set(f.vars) | {"z"}):
            Dx_E_f = E_f.derivative("x0")
            Dg_E_f = E_f_template.derivative("z")
            Dx_E_g = E_g.derivative("x0")
            assert abs( Dx_E_f - Dx_E_g*Dg_E_f) <= TOLERANCE 

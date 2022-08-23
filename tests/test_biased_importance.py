import sys; sys.path.append("..")

import binvec
import binfunc
import cgm 
from utils import generate_SRC_parameters, generate_module


TOLERANCE = 1e-10

vs = [ 
    cgm.omega, 
    cgm.nu
]

bz_vs = [ 
    cgm.get_value("Bz/DCGM"),
    cgm.get_value("Bz/RCGM")
]

def test_decomposition():
    '''
        check that 

            Bz_x(v_f) = (|~v_f0 & v_f1|/2^{|F - G|})*Bz_x(v_g)

        whenever f is monotone modular in g, f1 and f0 are the cofactors of f wrt g

        hash: hhjfq9K1Fd 
    '''
    for _ in range(100):
        f,g,f1,f0 = generate_module(3, 3, monotone=True)
        for v in vs:
            coeff = 0
            for S in binvec.itersets(f.vars - g.vars):
                coeff += not v(S, f0) and v(S, f1)
            coeff = coeff/2**(len(f.vars - g.vars))
            assert abs( cgm.banzhaf(v, "x0", f) - coeff*cgm.banzhaf(v, "x0", g) ) <= TOLERANCE


def test_SRC_weak():
    '''
        check that 

            Bz_y(v_f) >= Bz_x(v_f)

        where 
            - f is monotonically modular in g and h,
            - g = pi(h^S) for a renaming pi and S subset H,
            - x in H
            - y = pi(x) in G
            - g is a substitute for h in f

        hash: ANYgXi6U8c
    '''
    for _ in range(10):
        f,_,_,_,_,x,y = generate_SRC_parameters(2,3,strong=False)
        for bz_v in bz_vs:
            assert bz_v(y, f) >= bz_v(x, f) - TOLERANCE

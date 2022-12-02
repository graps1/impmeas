import impmeas as imp
from utils import X,Y

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
        Xss,Yss = X[:4],Y[:4]
        f = imp.random_table(Xss)
        pi = { x:y for x,y in zip(Xss,Yss)}
        S = imp.random_subset(Xss)
        h = f.flip(S).replace(pi)
        # there might be some rounding errors, so check if the values are "close enough"
        for rho in rhos:
            diff1 = imp.blame(f,"x0", rho=rho) - imp.blame(h, pi["x0"], rho=rho)
            diff2 = imp.blame(f, "x0", rho=rho) - imp.blame(~f, "x0", rho=rho)
            assert abs(diff1) <= TOLERANCE
            assert abs(diff2) <= TOLERANCE


def test_blame_nonincreasing_importance():
    '''
        checks whether the importance of a variable decreases if a function is 
        extended monotonically

        hash: U7jbpmrlnt
    '''
    for _ in range(100):
        f,h,_,_ = imp.random_module(X[:3],Y[:2],monotone=True)
        for rho in rhos:
            b1 = imp.blame(h, "x0", rho)
            b2 = imp.blame(f, "x0", rho)
            assert b1 >= b2 - TOLERANCE


# def test_blame_equiv_vars():
#     '''
#         checks whether the blame fulfills property SRC^S 
#         property
# 
#         hash: Scjxa9Mk6I
#     '''
#     for _ in range(10):
#         f,_,_,_,_,x,y = generate_SRC_parameters(2,3,strong=True)
#         for rho in rhos:
#             b1 = blame.blame(x, f, rho=rho)
#             b2 = blame.blame(y, f, rho=rho)
#             assert b2 >= b1 - TOLERANCE


def test_influence_NIM_MRP():
    '''
        checks whether the Influence can be decomposed as 

            - Inf_x(f) = Inf_h(f) * Inf_x(h)
        
        and whether it fulfills

            - Inf_x(f) <= Inf_x(h)
            - Inf_x(h) >= Inf_y(h) implies Inf_x(f) >= Inf_y(f)

        whenever f is modular in h.

        hash: wqIvk7atKj
    '''
    for _ in range(100):
        f,g,f1,f0 = imp.random_module(X[:3], Y[:3])
        f_template = imp.Table.var("z").ite(f1,f0)
        x, y = "x0", "x1"
        bfx = imp.influence(f, x)
        bgx = imp.influence(g, x)
        bgf = imp.influence(f_template, "z")
        assert abs( bgf*bgx - bfx) <= TOLERANCE
        assert bgx >= bfx - TOLERANCE

        bfy = imp.influence(f, y)
        bgy = imp.influence(g, y)
        if bgy > bgx:
            assert bfy >= bfx - TOLERANCE
        else:
            assert bfx >= bfy - TOLERANCE

        
            



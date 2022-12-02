import impmeas as imp

TOLERANCE = 1e-10

vs = [ 
    imp.dominating_cgm,
    imp.rectifying_cgm
]

def test_decomposition():
    '''
        check that 

            Bz_x(v_f) = Bz_g(v_f)*Bz_x(v_g)

        whenever f is monotone modular in g, f1 and f0 are the cofactors of f wrt g

        hash: hhjfq9K1Fd 
    '''
    for _ in range(100):
        X = [f"x{i}" for i in range(3)]
        Y = [f"y{i}" for i in range(3)]
        f,g,f1,f0 = imp.random_module(X,Y,monotone=True)
        f_template = imp.Table.var("z").ite(f1,f0)
        for v in vs:
            left = imp.banzhaf(v(f), "x0")
            right = imp.banzhaf(v(g), "x0")*imp.banzhaf(v(f_template), "z")
            assert abs(left - right ) <= TOLERANCE


# def test_SRC_weak():
#     '''
#         check that 
# 
#             Bz_y(v_f) >= Bz_x(v_f)
# 
#         where 
#             - f is monotonically modular in g and h,
#             - g = pi(h^S) for a renaming pi and S subset H,
#             - x in H
#             - y = pi(x) in G
#             - g is a substitute for h in f
# 
#         hash: ANYgXi6U8c
#     '''
#     for _ in range(10):
#         f,g,f1,f0 = imp.random_module(X,Y,monotone=True)
#         f_template = imp.Table.var("z").ite(f1,f0)
#         f,_,_,_,_,x,y = generate_SRC_parameters(2,3,strong=False)
#         for bz_v in bz_vs:
#             assert bz_v(y, f) >= bz_v(x, f) - TOLERANCE

def test_SUD():
    '''
        check that 

            Bz_x(v_f) >= Bz_x(v_h)

        where 
            - f, h is monotonically modular in g,
            - f_{g/1} >= h_{g/1} and f_{g/0} <= h_{g/0}
            - x in dep(g)
    '''
    for _ in range(50):
        X = [f"x{i}" for i in range(3)]
        Y = [f"y{i}" for i in range(3)]
        g = imp.random_table(X) 
        f0 = imp.random_table(Y) 
        h0 = imp.random_table(Y) | f0  # h0 >= f0
        h1 = imp.random_table(Y) | h0  # h1 >= h0 <= f1
        f1 = imp.random_table(Y) | h1  # f1 >= h1
        h = g.ite(h1,h0)
        f = g.ite(f1,f0)
        for v in vs:
            assert imp.banzhaf(v(f), "x0") >= imp.banzhaf(v(h), "x0") - TOLERANCE
import impmeas as imp

vs = [ imp.dominating_cgm, imp.rectifying_cgm ]

def test_monotonicity():
    '''
        checks whether the biased CGMs are monotone

        hash: sQ2uh27sJS
    '''
    for _ in range(100):
        f = imp.random_table([f"x{idx}" for idx in range(3)])
        S = imp.random_subset(f.vars)
        T = imp.random_subset(S)
        S, T = imp.set2ass(S,f.vars), imp.set2ass(T,f.vars)
        for v in vs:
            cg = v(f)
            assert cg[S] >= cg[T], (cg, S, T)


def test_equality_for_monotonic_functions():
    '''
        checks whether the biased CGMs agree for monotone boolean functions

        hash: 8hzE6SxRKD
    '''
    for _ in range(100):
        F = [ f"x{idx}" for idx in range(5) ]
        f = imp.random_table(F, monotone=True)
        for S in imp.iter_assignments(F):
            assert f[S] == imp.dominating_cgm(f)[S] == imp.rectifying_cgm(f)[S]


def test_quantifier_swap_for_monotone_extensions():
    '''
        checks whether 

            Exists G. Forall T. f =  Forall T. Exists G. f 

        assuming f is monotonically modular in g, T subset F - G

        hash: AW0bTa1qHX
    '''
    for _ in range(100):
        X = { f"x{idx}" for idx in range(3) }
        Y = { f"y{idx}" for idx in range(4) }
        f,_,_,_ = imp.random_module(list(X),list(Y),monotone=True)
        T = imp.random_subset(Y-X)
        assert f.forall(T).exists(X) == f.exists(X).forall(T) 


def test_decomposition():
    '''
        checks whether 

            v_f = (v_g & v_f1) | v_f0

        holds, given F cup (G cap H) = emptyset and g >= h

        hash: smuV9vBwJ8 
    '''
    for _ in range(100):
        X = [f"x{idx}" for idx in range(3)]
        Y = [f"y{idx}" for idx in range(4)]
        f,g,f1,f0 = imp.random_module(X,Y,monotone=True)
        for v in vs:
            assert v(f) == v(g) & v(f1) | v(f0)

def test_difference():
    '''
        checks whether 

            Dx v_f = (Dx v_g) * (Dg v_f)

        holds, given F cup (G cap H) = emptyset and g >= h

        hash: kBvOloehVe
    '''
    for _ in range(100):
        X = [f"x{idx}" for idx in range(3)]
        Y = [f"y{idx}" for idx in range(4)]
        f,g,f1,f0 = imp.random_module(X,Y,monotone=True)
        f_template = imp.Table.var("z").ite(f1,f0)
        for v in vs:
            Dx_v_f = v(f).derivative("x0") 
            Dx_v_g = v(g).derivative("x0")
            Dg_v_f = v(f_template).derivative("z")
            assert Dx_v_f == Dx_v_g & Dg_v_f


def test_type_invariance():
    '''
        checks whether

            v(T, h) = v(pi(T), g)
    
        holds for all T, assuming that g is the (pi, S)-equivalent of h

        hash: hY1Wmc2eBg
    '''
    for _ in range(100):
        X = [f"x{idx}" for idx in range(6)]
        Y = [f"y{idx}" for idx in range(6)]
        h = imp.random_table(X)
        S = imp.random_subset(X)
        pi = {x:y for x,y in zip(X,Y)}
        g = h.flip(S).replace(pi)
        for v in vs:
            v_h, v_g = v(h), v(g)
            for T in imp.iter_assignments(X):
                piT = { pi[x]: T[x] for x in T }
                assert v_h[T] == v_g[piT]

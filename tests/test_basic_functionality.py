import impmeas as imp
    
imp.formulas.set_pmc_solver(imp.formulas.GPMC())
imp.formulas.set_buddy_context(list("xyzvw"))

Rs = [ imp.Table, imp.Formula, imp.BuddyNode ]

def test_compositions():
    for R in Rs:
        f0 = R.parse("x & (y ^ z)")
        assert f0.boolean_derivative("x").equivalent(R.parse("y ^ z"))
        f1 = f0 | R.parse("x")
        assert f1.equivalent(R.parse("x"))
        l00, l01, l10, l11 = f0.branch("x", "y")
        assert l00.equivalent(R.parse("0"))
        assert l01.equivalent(R.parse("0"))
        assert l10.equivalent(R.parse("z"))
        assert l11.equivalent(R.parse("~z"))

        assert f0.expectation() == 0.25
        assert f0.flip("x").equivalent(R.parse("~x & (y ^ z)"))
        if R in [imp.Table, imp.Formula]:
            assert f0.replace({"x":"y", "y":"x"}).equivalent(R.parse("y & (x ^ z)"))

        if R == imp.Formula:
            assert f1.equivalent(R.parse("x & (y ^ z) | x"))

def test_pseudo_boolean():
    f0 = imp.Table.parse("x & (y ^ z)")
    x,z = imp.Table.var("x"), imp.Table.var("z")
    assert f0.derivative("y").equivalent(x*(1-2*z))
    assert (f0**2).equivalent(f0)
    assert (1-f0).equivalent(~f0)
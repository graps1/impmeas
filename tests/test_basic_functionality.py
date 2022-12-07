import impmeas as imp
    
imp.formulas.set_pmc_solver(imp.formulas.GPMC())
imp.formulas.set_buddy_context(list("xyzvw"))

Rs = [ imp.Table, imp.Formula, imp.BuddyNode ]

def test_compositions():
    for R in Rs:
        f0 = R.parse("x & (y ^ z)")
        assert f0.boolean_derivative("x") == R.parse("y ^ z")
        f1 = f0 | R.parse("x")
        assert f1 == R.parse("x")
        l00, l01, l10, l11 = f0.branch("x", "y")
        assert l00 == R.parse("0")
        assert l01 == R.parse("0")
        assert l10 == R.parse("z")
        assert l11 == R.parse("~z")

        assert f0.expectation() == 0.25
        assert f0.flip("x") == R.parse("~x & (y ^ z)")
        if R in [imp.Table, imp.Formula]:
            assert f0.replace({"x":"y", "y":"x"}) == R.parse("y & (x ^ z)")

        if R == imp.Formula:
            assert f1 == R.parse("x & (y ^ z) | x")

def test_pseudo_boolean():
    f0 = imp.Table.parse("x & (y ^ z)")
    x,z = imp.Table.var("x"), imp.Table.var("z")
    assert f0.derivative("y") == x*(1-2*z)
    assert f0**2 == f0
    assert 1-f0 == ~f0
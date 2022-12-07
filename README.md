A framework for operations on Boolean functions and importance measures. 

| Value | Table based | BDD based (Buddy) | #SAT based (GPMC) |
|--|--|--|--|
| Banzhaf | &#10004; | &#10004; | &#10004;
| Shapley | &#10004; | &#10007; | &#10007; 
| Influence | &#10004; | &#10004; | &#10004;
| Blame | &#10004; | &#10004; | &#10004; (via PMC)

| Coalition Game Mapping | Table based | BDD based (Buddy) |
|--|--|--|
| Dominating CGM | &#10004; | &#10004;
| Rectifying CGM | &#10004; | &#10004;
| HKR's CGM | &#10004;  | &#10007;

## Usage

Installation via

	python3 setup.py install

Requires lark for parsing formulas (https://github.com/lark-parser/lark).

### Table based representations

No further packages are required. One can instantiate Boolean functions represented by tables (i.e. a column vectors of size $2^n$) as follows:

```python
	import impmeas as imp 
	f = imp.Table.parse("x & (y ^ z)")
	g = imp.Table.parse("x | z")
	h = g | f # output: x | y ## this is simply a minimal form according to Quine-McCluskey
	print(h.expectation()) # output: 3/2^2 = 0.75. the relative number of true points.
```

More methods that can be called on all representations of Boolean functions (even Formulas and BDDs):

```python
	f = imp.Table.parse("x & (y ^ z)")
	f.boolean_derivative("y") # outputs: x. 
	f.derivative("y") # outputs: a pseudo Boolean function equivalent to x*(1-2*z)
	f.is_boolean # outputs: True	
	f.exists({"x"}) # outputs: a Boolean function equivalent to y^z
	f.forall({"x"}) # outputs: a Boolean function equivalent to 0
	f0, f1 = f.branch("x") # outputs: the cofactors of f w.r.t. x with f0 = 0 and f1 = y^z
	f.flip("x") # outputs: a Boolean function equivalent to ~x & (y^z)
	f.replace({"x":"v"}) # outputs: a Boolean functions equivalent to v & (y^z)
	f.prime_implicants() # outputs: [{'y': True, 'x': True, 'z': False}, {'y': False, 'x': True, 'z': True}] ## a list of f's prime implicants
	f.set_print_mode("table") # whether one wants to print Boolean functions as tables
	f.set_print_mode("primes") # whether one wants to print Boolean functions as a disjunction of their prime implicants 
```

It is possible to represent pseudo Boolean functions using tables (and only tables):

```python
	f = imp.Table.parse("x")
	g = imp.Table.parse("y")
	print( (3+g-f)**0.5 ) # outputs: a Table with floating point entries
```

The computation of importance values such as CHK's Blame, the Influence and Banzhaf + Shapley values is supported as well,

```python
	imp.blame(f, "x", rho=lambda n: 1/(n+1)) # output: 0.625
	imp.influence(f, "x") # output: 0.5
	imp.banzhaf(f, "y") # output: 0.0
	imp.shapley(f, "y") # output: -0.166..
```

Here, Banzhaf and Shapley values are computed by interpreting assignments as subsets via the characteristic mapping. Compute coalition game mappings as follows:

```python
	omega_f = imp.dominating_cgm(f) # output: instance of imp.Table with omega_f = xyz
	nu_f = imp.rectifying_cgm(f) # output: instance of imp.Table with nu_f = zx | xy
	hkr_f = imp.hkr_cgm(f, kappa=lambda z: 4*(z-0.5)**2) # output: instance of imp.Table with floating point entries
	imp.banzhaf(omega_f, "y") # output: 0.25
	imp.banzhaf(nu_f, "y") # output: 0.25
	imp.banzhaf(hkr_f, "y") # output: 0.1875
```

### Formula based representations

Also doesn't require more packages. Only Boolean operations are supported. We represent Boolean functions by formulas, e.g.

```python
	import impmeas as imp 
	f = imp.Formula.parse("x & (y ^ z)")
	g = imp.Formula.parse("x | z")
	h = g | f # output: x&(y^z)|(x|y) ## note that no simplifications are made
	h.expectation() # output: 3/2^2 = 0.75. the relative number of true points. (this is always exponential in the number of variables.)
	# + warning that solver not initialized
```

Efficiency can be gained by installing the GPMC model counter (https://git.trs.css.i.nagoya-u.ac.jp/k-hasimt/GPMC/-/tree/master) and then linking it by using 

```python
	import impmeas as imp
	solver = imp.formulas.GPMC(src='/usr/local/bin/gpmc', tmp_filename='/tmp/dimacs.cnf', bj=True, cs=3500) # here, /usr/local/bin/gpmc is the directory of the GPMC binary
	imp.formulas.set_pmc_solver(solver)
	f = imp.Formula.parse("x & (y ^ z)")
	print(f.expectation()) # output: 0.25. expected value of f without warning
```

The computation of Blame, Influence and Blame values via (projected) model counting is supported.

### BDD based representations 

We can use Buddy (https://buddy.sourceforge.net/manual/main.html, https://github.com/jgcoded/BuDDy) to represent Boolean functions using BDDs. Only Boolean operations are supported:

```python
	import impmeas as imp 
	imp.formulas.set_buddy_context(list("xyz"), lib="/usr/local/lib/libbdd.so") # specify the used variables and their order and the library beforehand
	f = imp.BuddyNode.parse("x & (y ^ z)")
	g = imp.BuddyNode.parse("x | z")
	h = g | f # output: <impmeas.formulas.buddy.BuddyNode at ....> 
	h.expectation() # output: 3/2^2 = 0.75. the relative number of true points.
	f.var_profile # output: { 'x': 1, 'y': 1, 'z': 2 } ## the number of nodes per variable
	f.dump("/tmp/f.pdf") # creates a pdf that displays f (nodes are labeled with the corresponding variable index)
```

The dominating and rectifying coalition game mappings can be represented using BDDs as follows:

```python
	f = imp.BuddyNode.parse("x & (y ^ z)")
	imp.dominating_cgm(f) # output: <impmeas.formulas.buddy.BuddyNode at ....>  representing the function x&y&z
	imp.rectifying_cgm(f) # output: <impmeas.formulas.buddy.BuddyNode at ....>  representing the function x&(y|z)
```

Banzhaf, Influence and Blame values can be computed relatively efficiently using BDDs.
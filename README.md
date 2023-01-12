A framework for operations on Boolean functions and importance measures. 

| Value | Table based | BuDDy | GPMC |
|--|--|--|--|
| Banzhaf | &#10004; | &#10004; | &#10004;
| Shapley | &#10004; | &#10007; | &#10007; 
| Influence | &#10004; | &#10004; | &#10004;
| CHK's Blame | &#10004; | &#10004; | &#10004;
| modified Blame | &#10004; | &#10004; | &#10004;

| Coalition Game Mapping | Table based | BuDDy |
|--|--|--|
| Dominating CGM | &#10004; | &#10004;
| Rectifying CGM | &#10004; | &#10004;
| HKR's CGM | &#10004;  | &#10007;

## Usage

Installation via

	python3 setup.py install

Requires lark for parsing formulas (https://github.com/lark-parser/lark).

### Table based representations

One can instantiate Boolean functions represented by tables (i.e. a column vectors of size $2^n$) as follows:

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
	f.derivative("x") == imp.Table.parse("z ^ y") # outputs: True ## checks for semantic equality (ditto for BDDs)
	f.exists({"x"}) # outputs: a Boolean function equivalent to y^z
	f.forall({"x"}) # outputs: a Boolean function equivalent to 0
	f0, f1 = f.branch("x") # outputs: the cofactors of f w.r.t. x with f0 = 0 and f1 = y^z
	f.flip("x") # outputs: a Boolean function equivalent to ~x & (y^z) ## only implemented for Table and Formula
	f.replace({"x":"v"}) # outputs: a Boolean functions equivalent to v & (y^z)
	f.prime_implicants() # outputs: [{'y': True, 'x': True, 'z': False}, {'y': False, 'x': True, 'z': True}] ## a list of f's prime implicants
	f.set_print_mode("table") # whether one wants to print Boolean functions as tables
	f.set_print_mode("primes") # whether one wants to print Boolean functions as a disjunction of their prime implicants 
	x = imp.Table.parse("x")
	f.equivalent(x & f1 | ~x & f0) # output: True ## checks for semantic equivalence 
```

It is possible to represent pseudo Boolean functions using tables (and only tables):

```python
	f = imp.Table.parse("x")
	g = imp.Table.parse("y")
	print( (3+g-f)**0.5 ) # outputs: a Table with floating point entries
```

The computation of importance values such as the (modified) Blame, the Influence and Banzhaf + Shapley values is supported as well,

```python
	f = imp.Table.parse("x & (y ^ z)")
	imp.blame(f, "x", rho=lambda n: 1/(n+1)) # output: 0.625
	imp.blame(f, "x", rho=lambda n: 1/(n+1), modified=True) # output: 0.75
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
	h = g | f # output: (x|z)|x&(y^z) ## note that no simplifications are made
	h == imp.Formula.parse("(x|z)|x&(y^z)") # output: True ## structural equality
	h == imp.Formula.parse("x|(z|x&(y^z))") # output: False
	h.expectation() # output: 3/2^2 = 0.75. the relative number of true points. (this is always exponential in the number of variables.)
	# + warning that solver not initialized
```

Efficiency can be gained by installing the GPMC model counter (https://git.trs.css.i.nagoya-u.ac.jp/k-hasimt/GPMC/-/tree/master) and then linking it by using 

```python
	import impmeas as imp
	solver = imp.GPMC(src='/usr/local/bin/gpmc', tmp_filename='/tmp/dimacs.cnf', bj=True, cs=3500) # here, /usr/local/bin/gpmc is the directory of the GPMC binary
	imp.set_pmc_solver(solver)
	f = imp.Formula.parse("x & (y ^ z)")
	print(f.expectation()) # output: 0.25. expected value of f without warning
```

The computation of Blame, Influence and Blame values via (projected) model counting is supported.

### BDD based representations 

We can use Buddy (https://buddy.sourceforge.net/manual/main.html, https://github.com/jgcoded/BuDDy) to represent Boolean functions using BDDs. Only Boolean operations are supported:

```python
	import impmeas as imp 
	imp.buddy_initialize(list("xyz"), lib="/usr/local/lib/libbdd.so") # specify the used variables and their order and the library beforehand
	f = imp.BuddyNode.parse("x & (y ^ z)")
	g = imp.BuddyNode.parse("x | z")
	h = g | f # output: <impmeas.formulas.buddy.BuddyNode at ....> 
	h.expectation() # output: 3/2^2 = 0.75. the relative number of true points.
	f.var_profile # output: { 'x': 1, 'y': 1, 'z': 2 } ## the number of nodes per variable
	f.dump("/tmp/f.pdf") # creates a pdf that contains the BDD for f (nodes are labeled with the corresponding variable index)
```

The dominating and rectifying coalition game mappings can be represented using BDDs as follows:

```python
	f = imp.BuddyNode.parse("x & (y ^ z)")
	imp.dominating_cgm(f) # output: <impmeas.formulas.buddy.BuddyNode at ....>  representing the function x&y&z
	imp.rectifying_cgm(f) # output: <impmeas.formulas.buddy.BuddyNode at ....>  representing the function x&(y|z)
```

Banzhaf, Influence and Blame values can be computed relatively efficiently using BDDs.

## Examples

Can be found under `impmeas/notebooks`.

* `examples.ipynb` consists of multiple examples that show how one can compute importance values using Buddy, GPMC or simple table based representations.
* `HKR_constancy_measures.ipynb` renders HKR's constancy measures.
* `special_class_of_functions.ipynb` contains a class of Boolean functions that introduces a lot of "disagreement" between different importance value functions.
* `statistics.ipynb` contains a benchmark that measures how fast importance values can be computed.

## Parsing Formulas 

Parsing formulas using lark is quite slow for larger formulas. It is advised to use

```python
	x,y,z = imp.Formula.var("x"), imp.Formula.var("y"), imp.Formula.var("z")
	f = x & (y ^ z)
	print(f) # output: x&(y^z)
```

or comparable instead. One can also enter already parsed formulas as tree, like so:

```python
	variable = ("V", "x")
	constant = ("C", "0") # or ("C", "1")
	composition = ("&", variable, constant)
	negation = ("~", composition)
	f = imp.Formula.parse(negation)
	print(f) # output: ~(x&0)
```
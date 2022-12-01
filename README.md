A framework for (symbolic) operations on boolean functions and importance measures.

**TODO**

- Requirements
	- bidict, sympy, tabulate, scipy
- Structure of repository
- Examples
	- Function from lambda
	- Random functions, modules, vectors, renamings, etc.
	- Compositions of functions
	- Importance values
		- Blame, different rhos
		- CGMs, how to obtain them from code
	- Rankings
		- Ranking from value 
		- Equality of rankings
- Add thesis if finished
- Comments in code

| Value | Table based | BDD based (Buddy) | #SAT based (GPMC) |
|--|--|--|--|
| Banzhaf | &#10004; | &#10004; | &#10004;
| Shapley | &#10004; | Not yet | Not yet 
| Influence | &#10004; | &#10004; | &#10004;
| Blame | &#10004; | &#10004; | &#10004; (via PMC)
| Omega | &#10004; | &#10004; | &#10007;
| Upsilon  | &#10004; | &#10004; | &#10007;
| Bz/Hammer | &#10004;  | &#10007; |  &#10007;

Ideas

* Given a weighted game $v[w_1,\dots,w_n; \tau]$, where $w_k$ is the weight of player $k$ and $\tau$ the threshold, develop a boolean circuit that computes $v$. This is should be doable with $n$ and $m = \lceil \log_2 \sum_{k=1}^n w_k \rceil$ $m$-bit adders. This should improve the applicability wrt game theoretic approaches.
* Is there a way to compute the Shapley value for a function with only one call to a #SAT solver?
* Give a way to compute the Shapley value via BDDs
* Fault tree analysis
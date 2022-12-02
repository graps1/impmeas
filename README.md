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
| Shapley | &#10004; | &#10007; | &#10007; 
| Influence | &#10004; | &#10004; | &#10004;
| Blame | &#10004; | &#10004; | &#10004; (via PMC)

| Coalition Game Mapping | Table based | BDD based (Buddy) |
|--|--|--|
| Dominating CGM | &#10004; | &#10004;
| Rectifying CGM | &#10004; | &#10004;
| HKR's CGM | &#10004;  | &#10007;

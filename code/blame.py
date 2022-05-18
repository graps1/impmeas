from binfunc import func
from binvec import vec, incidence, itervecs
from typing import Callable, Dict, Set, Tuple, List, Any

def k(u : vec, f : func, target_value=1) -> Set[str]:
  # returns the minimal number of flips needed in u 
  # to change the value of f[u] to `target_value`
  queue = [ set() ]
  u = u.restrict(f.vars)
  while len(queue) > 0:
    v = queue.pop(0)
    if f[u ^ incidence(v, f.vars)] == target_value:
      return len(v)
    else:
      neighbours = [ v.union({var}) for var in f.vars if var not in v ]
      queue += neighbours
  return float("inf")

def r(x : str, u : vec, f : func, c=None) -> Set[str]:
  if x not in f.vars:
    return float("inf")
  if c is None:
    c = f[u]
  u = u.restrict(f.vars)
  queue = [ set() ]
  while len(queue) > 0:
    v = queue.pop(0)
    uxorv = u ^ incidence(v, f.vars)
    if f[uxorv] == c and f[uxorv ^ incidence(x, f.vars)] != c:
      return len(v)
    else:
      neighbours = [ v | {y} for y in f.vars if y!=x and y not in v ]
      queue += neighbours
  return float("inf")

def blame(
    x : str,
    f : func, 
    rho : Callable[[float], float] = lambda x: 1/(x+1) 
  ) -> float:
  return sum( rho(r(x, vec, f)) for vec in itervecs(f.vars) )/2**f.varcount

def r_table(f : func) -> Tuple[List[List[int]], List[str]]:
  table, headers = f.table()
  headers += [ f"phi_{var}^u({f.name})" for var in f.vars_ordered ]
  for idx in range(len(table)):
    row = table[idx]
    u = vec({ f.vars_ordered[idx]: val for idx, val in enumerate(row[:-1]) })
    row += [ r(var, u, f) for var in f.vars_ordered ]
  return table, headers

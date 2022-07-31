from scipy.special import binom
from typing import Iterable, Set, Callable, List, Union
from .binfunc import func, init_empty
from .binvec import itervecs, vec

def forall(S: Set[str], f : func) -> func:
  assert isinstance(S, set)
  S = S & f.vars
  Fnew = f.vars - S
  ret = init_empty(Fnew)
  for u in itervecs(Fnew):
    ret[u] = all(f[ext] for ext in u.iterextensions(f.vars))
  return ret

def exists(S: Set[str], f : func) -> func:
  return ~forall(S, ~f)

def d( v : Callable[[Set[str], func], bool], S : Set[str], x : str, f : func) -> float:
  return v(S|{x}, f) - v(S, f)

def characteristic(S : Set[str], f : func) -> bool:
  assert S.issubset(f.vars)
  u = vec({ x: (x in S) for x in f.vars })
  return f[u] 

def omega(S : Set[str], f : func) -> bool:
  g = exists(S, forall(f.vars - S, f))
  return g[vec({})]

def nu(S : Set[str], f : func) -> bool:
  g = forall(f.vars - S, exists(S, f))
  return g[vec({})]

def hammer(S : Set[str], f: func, rho : Callable[[float], float] = lambda x: 4*(x-0.5)**2) -> float:
  ret = 0
  for alpha in itervecs(S):
    lamb = 0
    for u in alpha.iterextensions(f.vars):
      lamb += f[u]
    ret += rho( lamb*2**(len(S) - f.varcount) )
  return ret*2**(-len(S))

def sym(v : Callable[[Set[str], func], bool]) -> Callable[[Set[str], func], bool]:
  return lambda S,f: min(v(S,f), v(S,~f))

def crits(v : Callable[[Set[str], func], bool], x : str, f : func) -> Iterable[Set[str]]:
  # suppose v is monotone
  # ...add case when v is not monotone later
  # enumerate subsets not containing i in increasing order 
  tocheck_all = f.vars - {x}
  stack = [ (set(), tocheck_all, True) ]
  while len(stack) > 0:
    S, tocheck, check_i_crit = stack.pop()
    diff = v(S | { x }, f) - v(S, f)
    if check_i_crit and diff > 0:
      # print(v(S + [i], f), v(S, f))
      yield S, diff
    if len(tocheck)>0:
      # need to increase the size
      # find an efficient way to enumerate in non-repeating fashion!
      tocheck = tocheck.copy()
      y = tocheck.pop()
      stack.append(( S | { y }, tocheck, True ))
      stack.append(( S, tocheck, False ))

def banzhaf(v : Callable[[Set[str], func], bool], x : str, f : func) -> float:
  return sum(diff for _,diff in crits(v, x, f))/2**(f.varcount-1)

def shapley(v : Callable[[Set[str], func], bool], x : str, f : func) -> float:
  n = f.varcount
  return sum(diff/(n*binom(n-1, len(s))) for s,diff in crits(v,x,f))

def get_value(code : str) -> Callable[[str, func], float]:
  # code has form "Bz/DCGM" or "Sh/RCGM" or "Sh/QH"
  vals = code.split("/")
  assert len(vals) == 2
  assert vals[0] in ["Bz", "Sh"]
  assert vals[1] in ["DCGM", "RCGM", "SDCGM", "SRCGM", "QH"]
  importance = { "Bz": banzhaf, "Sh": shapley }[vals[0]]
  mapping = { 
    "DCGM": omega, 
    "RCGM": nu,
    "SDCGM": sym(omega),
    "SRCGM": sym(nu),
    "QH": hammer }[vals[1]]
  return lambda x,f: importance(mapping, x, f)

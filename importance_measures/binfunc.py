from __future__ import annotations

from sympy import Symbol
from typing import Callable, List, Iterator, Set, Tuple
from math import log2
import inspect
import random
from itertools import product
from tabulate import tabulate
from bidict import bidict

from .binvec import vec, itervecs, list2binvec, incidence, sum_notation
from .bintools import iterbin

class func:
  __f : List[bool]
  __vars : List[str]
  __name : str
  __vars_set : Set[str]

  def __init__(self, f : List[bool], vars : List[str] = None, name : str = "f") -> None:
    self.__f = f
    self.__vars = vars
    if self.__vars is None:
      self.__vars = [f"x{idx}" for idx in range(int(log2(len(f))))]
    self.__vars_set = set(self.vars_ordered)
    self.__name = name
    assert 2**self.varcount == len(f), "size of f needs to be a power of 2"

  def __len__(self) -> int:
    return sum(x for x in self.__f) 

  def __hash__(self):
    return hash(str(self.__f))

  @property
  def vars_ordered(self) -> List[str]:
    return self.__vars
  
  @property
  def const_0(self) -> bool:
    return len(self) == 0
  
  @property 
  def const_1(self) -> bool:
    return len(self) == 2**self.varcount

  @property
  def vars(self) -> Set[str]:
    return self.__vars_set

  @property
  def varcount(self) -> int:
    return len(self.vars)

  @property
  def name(self) -> str:
    return self.__name  

  @name.setter
  def name(self, newname):
    self.__name = newname
  
  def __vec2idx__(self, vec : vec) -> int:
    ret = 0
    for idx, var in enumerate( self.vars_ordered ):
      ret += vec[var]*2**(self.varcount - idx - 1)
    return int(ret)

  def __getitem__(self, vec : vec) -> bool:
    assert self.vars.issubset(vec.vars)
    return int( self.__f[self.__vec2idx__(vec)] )
  
  def __setitem__(self, vec : vec, val : bool):
    assert vec.vars == self.vars
    self.__f[self.__vec2idx__(vec)] = val
  
  def table(self) -> Tuple[List[List[int]], List[str]]:
    headers = [var for var in self.vars_ordered] + [ self.__name ]
    table = [u + [self[list2binvec(u, self.vars_ordered)]] for u in iterbin(self.varcount)]
    return table, headers

  def __compose(self, other : func, 
    compose : Callable[[int, int], int], 
    newname : str) -> func:

    assert isinstance(other, func)
    shared_vars = self.vars_ordered + [v for v in other.vars_ordered if v not in self.vars]
    f = func([0 for _ in range(2**len(shared_vars))], shared_vars, name=newname)
    for v in itervecs(f.vars):
      f[v] = compose(self[v], other[v])
    return f

  def get_core(self) -> Iterator[str]:
    for var in self.vars:
      for u in itervecs(self.vars):
        if self[u] != self[u^incidence(var,self.vars)]:
          yield var 
          break 

  def cofactor(self, alpha : vec) -> func:
    alpha = alpha.restrict(self.vars)
    ret = init_empty(self.vars - alpha.vars, name=self.name+f"[{alpha}]")
    for u in itervecs(self.vars - alpha.vars):
      ret[u] = self[u // alpha]
    return ret

  def reduce_to_core(self) -> func:
    core = set(self.get_core())
    alpha = vec({x: 0 for x in self.vars - core})
    ret = self.cofactor(alpha)
    ret.name = self.name 
    return ret

  def __xor__(self, other) -> func:
    return self.__compose(other, lambda x,y: x != y, f"({self.__name} ^ {other.__name})")

  def __invert__(self) -> func:
    return func([1-self.__f[idx] for idx in range(2**self.varcount)],
      self.vars_ordered, 
      f"{self.__name}'")

  def __and__(self, other) -> func:
    return self.__compose(other, lambda x,y: x and y, f"({self.__name} & {other.__name})")
    
  def __or__(self, other) -> func:
    return self.__compose(other, lambda x,y: x or y, f"({self.__name} | {other.__name})" )

  def __repr__(self) -> str:
    if self.const_0:
      return "0"
    elif self.const_1:
      return "1"
    else:
      return sum_notation(self.prime_implicants())
    # return tabulate(*self.table())
  
  def __le__(self, other) -> bool:
    assert isinstance(other, func)
    shared_vars = self.vars | other.vars
    return all(self[u] <= other[u] for u in itervecs(shared_vars))
  
  def __eq__(self, other) -> bool:
    return other <= self and self <= other

  def flip(self, S : Set[str]) -> func:
    # returns f^S if f is this function
    f_cpy = func(self.__f.copy(), self.vars_ordered.copy(), name = self.name+"^S")
    for u in itervecs(self.vars):
      uprime = u^incidence(S, self.vars)
      f_cpy[uprime] = self[u]
    return f_cpy

  def exists(self, S : Set[str]) -> func:
    # returns exists S. (this function)
    ret = init_empty(self.vars - S)
    for u in itervecs(S & self.vars):
      ret = ret | self.cofactor(u)
    return ret

  def forall(self, S : Set[str]) -> func:
    # returns forall S. (this function)
    return ~(~self).exists(S)

  def rename(self, pi : bidict[str, str]) -> func:
    # returns pi(f) if f is this function
    pi_vars = [ pi[x] for x in self.vars_ordered ]
    f_cpy = func(self.__f.copy(), pi_vars.copy(), name = "pi("+self.name+")")
    for u in itervecs(self.vars):
      uprime = u.rename(pi)
      f_cpy[uprime] = self[u]
    return f_cpy

  def prime_implicants(self) -> List[vec]:
    # the encoding is as follows:
    # - returns a list of prime implicants
    # - every implicant is a list itself with an entry for every variable
    # - if an entry takes the value -1, it means that that variable is not part of the implicant
    # - if an entry takes the value  0, it means that that variable occurs negatively in that implicant
    # - if an entry takes the value  1, it means that that variable occurs positively in that implicant
    us = [ vec for vec in itervecs(self.vars) if self[vec] == 1 ] 
    while True:
      # select resolvents
      marked = []
      for u1 in us:
        for u2 in us:
          # check if they can be resolved, i.e. if there exists EXACTLY one variable 
          # that occurs negatively in u1 and positively in u2 (or vice versa)
          # and all other variables have the same value
          if u1.vars != u2.vars:
            continue 
          difference = [ var for var in u1.vars if u1[var] != u2[var] ]
          if len(difference) == 1:
            # mark for resolution
            marked.append((u1, u2, difference[0]))

      # if resolvents exists.... resolve. otherwise, stop.
      if len(marked) == 0:
        break
      for (res1, res2, targetvar) in marked:
        if res1 in us:
          us.remove(res1)
        if res2 in us:
          us.remove(res2)
        new = res1.copy()
        new.remove(targetvar)
        if new not in us:
          us.append(new)
          # print(f"merging {res1} and {res2} to {new}")
          # print(f"remaining {us}")
    return us

def from_lambda(lambda_f) -> func:
  vars = inspect.getfullargspec(lambda_f).args
  bitcount = len(vars)
  f = func([0]*(2**bitcount), vars)
  for u in iterbin(bitcount):
    usymbols = [Symbol(x) for x in vars]
    v = list2binvec(u, vars)
    val = lambda_f(*usymbols)
    if not isinstance(val, int):
      val = bool( val.subs({ xsym: v[x] for xsym, x in zip(usymbols, vars) }) )
    f[v] = val
  return f

def init_empty(vars : Set[str], name : str = "f") -> func:
  f = [0 for _ in range(2**len(vars))]
  vars = sorted(vars)
  return func(f, vars = vars, name = name)

def from_implicant(u : vec, name : str = "f") -> func:
  f = init_empty(u.vars, name)
  f[u] = 1
  return f

def iterfunc(bits : int, random : bool = False,
             maxcount : int = None, 
             var_prefix : str = "x",
             include_funcs_with_less_bits = False) -> Iterator[func]:
  bits = [ bits ] if not include_funcs_with_less_bits else range(1,bits+1)
  if random: 
    for _ in range(maxcount):
      b = choice(bits)
      f = randfunc(2**b, var_prefix=var_prefix)
      yield f
  else:
    ctr = 0 
    for b in bits:
      for f in iterbin(2**b):
        if maxcount is not None and ctr >= maxcount:
          break 
        ctr += 1
        yield func(f, vars=[f"{var_prefix}{idx}" for idx in range(b)])

def randfunc(bits : int, var_prefix : str = "x", name : str = "f") -> func:
  f = next(iter(iterbin(2**bits, random=True, maxcount=1)))
  f = func(f, vars=[f"{var_prefix}{idx}" for idx in range(bits)], name=name)
  return f

def rand_substitute(varcount=3, varpref="z", monotone=False):
  '''
    returns a tuple 

      f11, f01, f10, f00

    of functions over { {varpref}0, ... {varpref}{varcount} } such that g forms a substitute for 
    h in

      f = h&g&f11 | h&~g&f10 | ~h&g&f01 | ~h&~g&g00
    
    whenever G&H=0
  '''
  # f_hg
  # f00 != f10 ===> f00 != f01 
  # f01 != f11 ===> f10 != f11
  choices = [
    (f11, f01, f10, f00) for f11, f01, f10, f00 in product([0,1],repeat=4) if \
    (f00 == f10 or f00 != f01) and (f01 == f11 or f10 != f11)
  ] if not monotone else [
    (f11, f01, f10, f00) for f11, f10, f01, f00 in product([0,1],repeat=4) if \
    (f00 == f10 or f00 != f01) and (f01 == f11 or f10 != f11) and \
    (f11 >= f01 >= f10 >= f00)
  ]
  Z = {f"{varpref}{idx}" for idx in range(varcount)}
  f00 = init_empty(Z)
  f10 = init_empty(Z)
  f01 = init_empty(Z)
  f11 = init_empty(Z)
  for u in itervecs(Z):
      c = random.choice(choices)
      f11[u] = c[0]
      f01[u] = c[1]
      f10[u] = c[2]
      f00[u] = c[3]
  return f11, f01, f10, f00
   

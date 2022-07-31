from __future__ import annotations

from typing import Iterator, List, Set, Tuple, Dict, Union
from bidict import bidict

from .bintools import iterbin
    
class vec:
  u: Dict[str, bool]

  def __init__(self, u: Dict[str, bool] = dict()) -> None:
    self.u = u

  @property
  def length(self) -> int:
    return len({ v for v in self.vars if self[v] == 1})

  @property
  def vars(self) -> Set[str]:
    return set(self.u.keys())

  def remove(self, var : str):
    del self.u[var]

  def restrict(self, var : Set[str]) -> vec:
    return vec({ k: v for k,v in self.u.items() if k in var })

  def rename(self, pi : bidict[str, str]) -> vec:
    return vec({ pi[x]: v for x,v in self.u.items() })

  def apply_switch(self, pi, S):
    piS = { pi[x] for x in S }
    H, G = set(pi.keys()), set(pi.values())
    u_H = self.restrict(H)
    u_G = self.restrict(G)
    u_Other = self.restrict(self.vars - (H|G))
    uprime_H = (u_G^incidence(piS, G)).rename(pi.inv)
    uprime_G = (u_H^incidence(S, H)).rename(pi)
    return uprime_H // uprime_G // u_Other

  def __repr__(self) -> str:
    return " ".join(f"{k}/{int(self.u[k])}" for k in sorted(self.u))

  def __hash__(self):
    return hash(str(self))

  def iterextensions(self, X : Set[str]):
    newvars = list( X - self.vars )
    if len(newvars) == 0:
      yield self
    else:
      for b in iterbin(len(newvars)):
        uprime = vec( { newvars[idx] : val for idx, val in enumerate(b) } )
        yield self // uprime


  def copy(self):
    return vec(self.u.copy())

  def __le__(self, other):
    if not isinstance(other, vec):
      return False
    if not self.vars == other.vars:
      return False
    return all(self.u[var] <= other.u[var] for var in self.vars)

  def __ge__(self, other):
    return other <= self
  
  def __eq__(self, other):
    return other <= self and self <= other

  def __getitem__(self, key):
    return self.u[key]

  def __setitem__(self, key, val):
    self.u[key] = val

  def __floordiv__(self, other) -> vec:
    if not isinstance(other, vec):
      other = vec(other)
    assert other.vars.intersection(self.vars) == set(), f"{self} and {other} not defined on distinct variables!"
    return vec( { **self.u, **other.u } )

  def __compose(self, other, compose) -> vec:
    assert isinstance(other, vec)
    assert other.vars == self.vars
    return vec({ var: compose(other[var], self[var]) for var in self.vars })

  def __xor__(self, other) -> vec:
    return self.__compose(other, lambda x,y: x != y)

  def __invert__(self) -> vec:
    return vec({ key: not val for key, val in self.u.items() })

  def __and__(self, other) -> vec:
    return self.__compose(other, lambda x,y: x and y)

  def __or__(self, other) -> vec:
    return self.__compose(other, lambda x,y: x or y)

def list2binvec(u : List[bool], vars : List[str]):
  assert len(u) == len(vars)
  return vec({ var: u[idx] for idx, var in enumerate(vars) })

def incidence(S : Union[str, Set[str]], X : Set[str]) -> vec:
  if not isinstance(S, set):
    return incidence({S}, X)
  assert S.issubset(X)
  return vec( { var: (var in S) for var in X } )

def itervecs(X : Set[str]) -> Iterator[vec]:
  for v in vec().iterextensions(X):
    yield v

def itersets(X : Set[str]) -> Iterator[Set]:
  for v in itervecs(X):
    yield { k for k,v in v.u.items() if v }

def sum_notation(us : List[vec]) -> str:
  els = []
  for u in us:
    l = ""
    for var, val in u.u.items():
      l += var
      if val == 0:
        l += "'" 
    els.append(l)
  return " + ".join(els)

def from_code(code : str) -> vec:
  els = code.split("/")
  dic = {}
  for el in els: 
    el = el.split("=")
    var = el[0]
    val = bool(int(el[1]))
    dic[var] = val
  return vec(dic)


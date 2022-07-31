from typing import Callable, List, Set, Union, Tuple, Dict
from dataclasses import dataclass
from .binfunc import func

@dataclass
class Ranking:
  ranking : List[Set[str]]
  values : Dict[str, float]
  is_valued : bool

  def __init__(self, ranking : List[Set[str]], values : Dict[str, float] = None):
    self.is_valued = values is not None
    self.values = values
    self.ranking = ranking

  def __getitem__(self, var):
    for block_idx, block in enumerate(self.ranking):
      if var in block:
        return block_idx
    assert False

  def __repr__(self):
    if self.is_valued:
      return " < ".join(' == '.join(f"{var}:{self.values[var]:.4f}" for var in vars) for vars in  self.ranking)
    else:
      return " < ".join([ " == ".join(vars) for vars in self.ranking ])

  def __eq__(self, other):
    return isinstance(other, Ranking) and other.ranking == self.ranking

def from_val(eval : Callable[[str, func], float], f : func, precision=8) -> Ranking:
  rank = sorted(
    [ (var, eval(var, f)) for var in f.vars ], 
    key=lambda tpl: tpl[1])
  ordered_partition, curset, lastval = [], set(), None
  values = {}
  for var, val in rank:
    if lastval is not None and abs(lastval - val) > 10**(-precision):
      ordered_partition.append( curset )
      curset = set()
    curset.add( var )
    values[var] = val
    lastval = val
  if len(curset) > 0:
    ordered_partition.append( curset )
  return Ranking(ordered_partition, values)

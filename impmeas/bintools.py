from typing import Iterator, List, Set, Tuple, Dict
from random import randint

def binary(idx : int, bitcount : int) -> List[int]:
  if bitcount == 0:
    return []
  else:
    return [int(c) for c in str(bin(idx))[2:].zfill(bitcount)]

def iterbin(bits, random=False, maxcount=None) -> Iterator[List[int]]:
  if maxcount is None:
    maxcount = 2**bits
  for idx in range(maxcount):
    if random:
      yield [bool(randint(0,1)) for _ in range(bits)]
    else:
      yield binary(idx, bits)

def itersets(bits, random=False, maxcount=None) -> Iterator[Set[int]]:
  for u in iterbin(bits, random=random, maxcount=maxcount):
    yield { idx for idx in range(bits) if u[idx]==1 }

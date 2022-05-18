
import cgm 
import blame
import numpy as np
from tqdm import tqdm
from ranking import from_val
from binfunc import func, iterfunc
from tabulate import tabulate

RANKINGS = [
  (blame.blame, "Blame"),
  (cgm.get_value("Bz/DCGM"), "Bz/DCGM"),
  (cgm.get_value("Bz/RCGM"), "Bz/RCGM"),
  (cgm.get_value("Bz/QH"), "Bz/QH")
]
RANKING_COUNT = len(RANKINGS)

def compare_rankings(f : func):
  rankings = [(from_val(val, f), name) for val, name in RANKINGS ]
  matrix = np.zeros((RANKING_COUNT, RANKING_COUNT)) 
  for idx1, (rank1, _) in enumerate(rankings):
    for idx2 in range(idx1, len(rankings)):
      rank2, _ = rankings[idx2]
      matrix[idx1, idx2] = int(rank1 == rank2)
  return matrix

def search(bitcount, random=True, maxiter=None, normalize=True):
  matrix = np.zeros((RANKING_COUNT, RANKING_COUNT))
  count_all = 0
  for f in tqdm(iterfunc(bitcount, random=random, maxcount=maxiter)):
    matrix += compare_rankings(f)
    count_all += 1
  if normalize:
    matrix /= count_all 
  return matrix

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--n", type=int, default=3)
  parser.add_argument("--search", type=str, default="random")
  parser.add_argument("--maxiter", type=int, default=1000)
  args = parser.parse_args()

  assert args.search in ["random", "systematic"], "search type not supported"
  if args.search == "random":
    m = search(args.n, random=True, maxiter=args.maxiter, normalize=True)
  else:
    m = search(args.n, random=False, normalize=True)

  names = list(name for _,name in RANKINGS)
  t = tabulate(
    [[name, *m[idx,:]] for idx, name in enumerate(names)],
    headers=[""] + names
  )
  print(t)
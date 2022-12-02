from .formulas import Formula, Table, BuddyNode, Repr
from .formulas.utils import iter_assignments
from .mapping import influence, banzhaf, shapley, blame, dominating_cgm, hkr_cgm, rectifying_cgm
from .convenient import random_assignment, random_table, random_subset, random_k_cnf, replace, set2ass, random_module
from .fallback import scs, d
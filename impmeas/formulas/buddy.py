import os
from ctypes import CDLL, c_double, c_int, c_char_p, byref, POINTER, cdll
from typing import Tuple, Union

from .repr import PseudoBoolFunc


class BuddyNode(PseudoBoolFunc):
	MUST_ALWAYS_BE_BOOLEAN = True

	def __init__(self, node_id : int):
		super().__init__()
		self.node_id = node_id
		self.__buddy_obj_instance_counter = BUDDY_OBJ_INSTANCE_COUNTER
		assert BUDDY_OBJ is not None, "Buddy not instantiated"
		BUDDY_OBJ.bdd_addref(self.node_id)

	# --- ABSTRACT METHODS ---

	def __getitem__(self, assignment: dict[str, bool]) -> bool: 
		if self == BuddyNode.true: return True
		elif self == BuddyNode.false: return False
		else:
			sub = self.high if assignment[self.topvar] else self.low
			return sub[assignment]

	def __hash__(self): 
		return self.node_id.__hash__()

	def __copy__(self): 
		return BuddyNode(self.node_id)

	def __del__(self):
		if BUDDY_OBJ_INSTANCE_COUNTER == self.__buddy_obj_instance_counter and BUDDY_OBJ is not None:
			BUDDY_OBJ.bdd_delref(self.node_id)

	@property
	def is_boolean(self):
		return True

	@property
	def vars(self) -> set[str]: 
		return set(v for v,c in self.var_profile.items() if c > 0)

	def cofactor(self, ass: dict[str, bool]) -> "BuddyNode": 
		r = BuddyNode.true
		for x in ass:
			xf = BuddyNode.var(x)
			if not ass[x]: xf = ~xf
			r = r & xf
		return BuddyNode(BUDDY_OBJ.bdd_restrict(self.node_id, r.node_id))

	def flip(self, S:Union[str,set[str]]) -> "BuddyNode":
		if isinstance(S,str): S = {S}
		g = self
		for x in S:
			f0, f1 = g.branch(x)
			g = BuddyNode.var(x).ite(f0, f1)
		return g

	@classmethod
	@property
	def false(cls) -> "BuddyNode": 
		return BuddyNode( BUDDY_OBJ.bdd_false())

	@classmethod
	@property
	def true(cls) -> "BuddyNode": 
		return BuddyNode( BUDDY_OBJ.bdd_true())

	@classmethod
	def _apply(cls, op: str, *children) -> "BuddyNode":
		if op in ('~'):
			u, = children
			return BuddyNode(  BUDDY_OBJ.bdd_not(u.node_id))
		elif len(children)==2:
			u, v = children
			if op in ('|'): return BuddyNode(  BUDDY_OBJ.bdd_or(u.node_id, v.node_id))
			elif op in ('&'): return BuddyNode(  BUDDY_OBJ.bdd_and(u.node_id, v.node_id))
			elif op in ('^'): return BuddyNode(  BUDDY_OBJ.bdd_xor(u.node_id, v.node_id))
			elif op in ('->'): return BuddyNode(  BUDDY_OBJ.bdd_imp(u.node_id, v.node_id))
			elif op in ('<->'): return BuddyNode(  BUDDY_OBJ.bdd_biimp(u.node_id, v.node_id))
		elif len(children) == 3 and op == "ite":
			u, v, w = children
			return BuddyNode(  BUDDY_OBJ.bdd_ite(u.node_id, v.node_id, w.node_id))
		raise Exception(f"operator {op} and children count #{len(children)} do not fit")

	@classmethod
	def var(cls, x: str) -> "BuddyNode": 
		if x not in VAR_NAME2LEVEL.keys():
			raise Exception(f"Variable {x} not found!")
		return BuddyNode( BUDDY_OBJ.bdd_ithvar(VAR_NAME2LEVEL[x]))

	## END ABSTRACT METHODS
	## OVERWRITTEN:

	def expectation(self) -> float: 
		return float(BUDDY_OBJ.bdd_satcount(self.node_id)) / 2**len(VARS)

	def __le__(self, other):
		raise NotImplementedError()

	def __ge__(self, other):
		raise NotImplementedError()

	def __eq__(self, other : "BuddyNode"): 
		return isinstance(other, BuddyNode) and self.node_id == other.node_id

	## END OVERWRITTEN

	# --- END ABSTRACT METHODS ---

	def ite(self, o1: "BuddyNode", o2: "BuddyNode") -> "BuddyNode": 
		return BuddyNode._apply("ite", self, o1, o2)

	@property
	def topvar(self) -> str:
		if self.node_id in [0,1]: return None
		return VARS[BUDDY_OBJ.bdd_var(self.node_id)]

	@property
	def low(self) -> "BuddyNode": 
		return BuddyNode(BUDDY_OBJ.bdd_low(self.node_id))

	@property
	def high(self) -> "BuddyNode": 
		return BuddyNode(BUDDY_OBJ.bdd_high(self.node_id))

	@property
	def nodecount(self) -> int:
		return BUDDY_OBJ.bdd_nodecount(self.node_id)

	@property
	def var_profile(self) -> dict[str, int]:
		# returns a variable-int-dictionary that counts how often variable nodes occur in this function
		profile = BUDDY_OBJ.bdd_varprofile(self.node_id)
		return { var: count for var, count in zip(VARS, profile.contents ) }
		
	def dump(self, filename="out.bdd"):
		if filename[-3:] == "dot":
			BUDDY_OBJ.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), self.node_id)
		if filename[-3:] == "pdf":
			tempf = filename+".tmp"
			BUDDY_OBJ.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), self.node_id)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		else:
			BUDDY_OBJ.bdd_fnsave(c_char_p(filename.encode("UTF-8")), self.node_id)
			with open(filename+"v", "w") as f:
				f.write("\n".join(VARS))
	
	@property 
	def level(self):
		if self.node_id in [0,1]: return len(VARS)
		var = BUDDY_OBJ.bdd_var(self.node_id)
		return BUDDY_OBJ.bdd_var2level(var)

BUDDY_OBJ = None
VARS = None
VAR_NAME2LEVEL = None
on_delete_cbs = []
BUDDY_OBJ_INSTANCE_COUNTER = 0

def buddy_initialize(vars: list[str], lib:str ="/usr/local/lib/libbdd.so", nodenum=1<<20, cachesize=1<<15) -> None: 
	global BUDDY_OBJ, VARS, VAR_NAME2LEVEL, on_delete_cbs, BUDDY_OBJ_INSTANCE_COUNTER

	if BUDDY_OBJ is not None:
		for cb in on_delete_cbs: cb()
		BUDDY_OBJ.bdd_done()
		BUDDY_OBJ_INSTANCE_COUNTER += 1

	VARS = tuple(vars)
	VAR_NAME2LEVEL = { x : k for k, x in enumerate(vars) }

	BUDDY_OBJ = CDLL(lib)
	BUDDY_OBJ.bdd_init(nodenum, cachesize)
	BUDDY_OBJ.bdd_setvarnum(c_int(len(vars)))
	BUDDY_OBJ.bdd_varprofile.restype = POINTER(c_int * len(vars))
	BUDDY_OBJ.bdd_satcount.restype = c_double
	BUDDY_OBJ.bdd_setmaxincrease(1<<27)
	BUDDY_OBJ.bdd_setcacheratio(32)
	BUDDY_OBJ.bdd_swapvar.restype = c_int
	BUDDY_OBJ.bdd_autoreorder.restype = c_int
	BUDDY_OBJ.bdd_varblockall()

def add_buddy_delete_callback(method):
	on_delete_cbs.append(method)

def swap_vars(v1, v2):
	assert v1 in VAR_NAME2LEVEL
	assert v2 in VAR_NAME2LEVEL
	id1, id2 = VAR_NAME2LEVEL[v1], VAR_NAME2LEVEL[v2]
	BUDDY_OBJ.bdd_swapvar(id1, id2)	
	BUDDY_OBJ.bdd_printorder()

def set_dynamic_reordering(type=True):
	if type:
		BUDDY_OBJ.bdd_autoreorder(3) # sifting as standard reordering
		BUDDY_OBJ.bdd_enable_reorder()
	else:
		BUDDY_OBJ.bdd_disable_reorder()

def reorder(method=3):
	rnames = {
		1:"WIN2", 
		2:"WIN2ITE", 
		3:"SIFT", 
		4:"SIFTITE", 
		5:"WIN3", 
		6:"WIN3ITE", 
		7:"RANDOM"}
	print("reorder via",rnames[method])
	BUDDY_OBJ.bdd_reorder(method)

def load(fil, vars) -> Tuple["BuddyContext", BuddyNode]:
	# returns new root node of read bdd
	# print(f"load {fil} ...")
	root = c_int()
	buddy_initialize(vars)
	BUDDY_OBJ.bdd_fnload(c_char_p(fil.encode("UTF-8")), byref(root))
	BUDDY_OBJ.bdd_addref(root.value)
	# print(f"loaded {fil}")
	return BUDDY_OBJ, BuddyNode(root.value)

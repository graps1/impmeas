import os
from ctypes import CDLL, c_double, c_int, c_char_p, byref, POINTER
from typing import Tuple, Union
from math import comb

from functools import cache

from .repr import PseudoBoolFunc


BUDDY_CONTEXT_INSTANCE:"BuddyContext" = None
def set_buddy_context(vars: list[str], lib:str ="/usr/local/lib/libbdd.so", nodenum=1<<28, cachesize=1<<20):
	global BUDDY_CONTEXT_INSTANCE
	if BUDDY_CONTEXT_INSTANCE: del BUDDY_CONTEXT_INSTANCE
	BUDDY_CONTEXT_INSTANCE = BuddyContext(vars, lib=lib, nodenum=nodenum, cachesize=cachesize)

class BuddyNode(PseudoBoolFunc):
	MUST_ALWAYS_BE_BOOLEAN = True

	def __init__(self, node_id : int):
		super().__init__()
		self.node_id = node_id
		assert BUDDY_CONTEXT_INSTANCE is not None, "Buddy not instantiated"
		BUDDY_CONTEXT_INSTANCE._bdd.bdd_addref(self.node_id)

	# --- ABSTRACT METHODS ---

	def __getitem__(self, assignment: dict[str, bool]) -> bool: 
		if self == BUDDY_CONTEXT_INSTANCE.true: return True
		elif self == BUDDY_CONTEXT_INSTANCE.false: return False
		else:
			sub = self.high if assignment[self.topvar] else self.low
			return sub[assignment]

	def __hash__(self): 
		return self.node_id.__hash__()

	def __copy__(self): 
		return BuddyNode(self.node_id)

	def __del__(self):
		if BUDDY_CONTEXT_INSTANCE is not None:
			BUDDY_CONTEXT_INSTANCE._bdd.bdd_delref(self.node_id)

	@property
	def is_boolean(self):
		return True

	@property
	def vars(self) -> set[str]: 
		return set(v for v,c in self.var_profile.items() if c > 0)

	def cofactor(self, ass: dict[str, bool]) -> "BuddyNode": 
		r = BUDDY_CONTEXT_INSTANCE.true
		for x in ass:
			xf = BUDDY_CONTEXT_INSTANCE.var(x)
			if not ass[x]: xf = ~xf
			r = r & xf
		return BuddyNode(BUDDY_CONTEXT_INSTANCE._bdd.bdd_restrict(self.node_id, r.node_id))

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
		return BUDDY_CONTEXT_INSTANCE.false

	@classmethod
	@property
	def true(cls) -> "BuddyNode": 
		return BUDDY_CONTEXT_INSTANCE.true	

	@classmethod
	def _apply(cls, op: str, *children) -> "BuddyNode":
		return BUDDY_CONTEXT_INSTANCE.apply(op, *children)

	@classmethod
	def var(cls, x: str) -> "BuddyNode": 
		return BUDDY_CONTEXT_INSTANCE.var(x)

	## END ABSTRACT METHODS
	## OVERWRITTEN:

	def expectation(self) -> float: 
		return float(BUDDY_CONTEXT_INSTANCE._bdd.bdd_satcount(self.node_id)) / 2**BUDDY_CONTEXT_INSTANCE.varcount

	def __le__(self, other):
		raise NotImplementedError()

	def __ge__(self, other):
		raise NotImplementedError()

	def __eq__(self, other : "BuddyNode"): 
		return isinstance(other, BuddyNode) and self.node_id == other.node_id

	## END OVERWRITTEN

	# --- END ABSTRACT METHODS ---

	def ite(self, o1: "BuddyNode", o2: "BuddyNode") -> "BuddyNode": 
		return BUDDY_CONTEXT_INSTANCE.apply("ite", self, o1, o2)

	@property
	def topvar(self) -> str:
		if self.node_id in [0,1]: return None
		return BUDDY_CONTEXT_INSTANCE.vars[BUDDY_CONTEXT_INSTANCE._bdd.bdd_var(self.node_id)]

	@property
	def low(self) -> "BuddyNode": 
		return BuddyNode(BUDDY_CONTEXT_INSTANCE._bdd.bdd_low(self.node_id))

	@property
	def high(self) -> "BuddyNode": 
		return BuddyNode(BUDDY_CONTEXT_INSTANCE._bdd.bdd_high(self.node_id))

	@property
	def nodecount(self) -> int:
		return BUDDY_CONTEXT_INSTANCE._bdd.bdd_nodecount(self.node_id)

	@property
	def var_profile(self) -> dict[str, int]:
		# returns a variable-int-dictionary that counts how often variable nodes occur in this function
		profile = BUDDY_CONTEXT_INSTANCE._bdd.bdd_varprofile(self.node_id)
		return { var: count for var, count in zip(BUDDY_CONTEXT_INSTANCE.vars, profile.contents ) }
		
	def dump(self, filename="out.bdd"):
		if filename[-3:] == "dot":
			BUDDY_CONTEXT_INSTANCE._bdd.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), self.node_id)
		if filename[-3:] == "pdf":
			tempf = filename+".tmp"
			BUDDY_CONTEXT_INSTANCE._bdd.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), self.node_id)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		else:
			BUDDY_CONTEXT_INSTANCE._bdd.bdd_fnsave(c_char_p(filename.encode("UTF-8")), self.node_id)
			with open(filename+"v", "w") as f:
				f.write("\n".join(BUDDY_CONTEXT_INSTANCE.vars))
	
	@property 
	def level(self):
		if self.node_id in [0,1]:
			return len(BUDDY_CONTEXT_INSTANCE.vars)
		var = BUDDY_CONTEXT_INSTANCE._bdd.bdd_var(self.node_id)
		return BUDDY_CONTEXT_INSTANCE._bdd.bdd_var2level(var)

class BuddyContext:
	def __init__(self, vars: list[str], lib:str ="/usr/local/lib/libbdd.so", nodenum=1<<28, cachesize=1<<20) -> None: 
		buddy = CDLL(lib)

		buddy.bdd_varprofile.restype = POINTER(c_int * len(vars))
		buddy.bdd_satcount.restype = c_double
		buddy.bdd_init(nodenum, cachesize)
		buddy.bdd_setmaxincrease(1<<27)
		buddy.bdd_setcacheratio(32)
		buddy.bdd_setvarnum(c_int(len(vars)))
		buddy.bdd_swapvar.restype = c_int
		buddy.bdd_autoreorder.restype = c_int
		buddy.bdd_varblockall()
		self._bdd = buddy

		# generate dict for varnames
		self.__vars = tuple(vars)
		self.__name2var_id = { x : k for k, x in enumerate(self.vars) }
		# self.__nodes = []

	# def register(self, node: BuddyNode):
	# 	self._bdd.bdd_addref(node.node_id)
	# 	self.__nodes.append(node)

	@property
	def false(self) -> BuddyNode:
		return BuddyNode( self._bdd.bdd_false())

	@property
	def true(self) -> BuddyNode:
		return BuddyNode( self._bdd.bdd_true())

	def apply(self, op : str, *children) -> BuddyNode:
		if op in ('~'):
			u, = children
			return BuddyNode(  self._bdd.bdd_not(u.node_id))
		elif len(children)==2:
			u, v = children
			if op in ('|'): return BuddyNode(  self._bdd.bdd_or(u.node_id, v.node_id))
			elif op in ('&'): return BuddyNode(  self._bdd.bdd_and(u.node_id, v.node_id))
			elif op in ('^'): return BuddyNode(  self._bdd.bdd_xor(u.node_id, v.node_id))
			elif op in ('->'): return BuddyNode(  self._bdd.bdd_imp(u.node_id, v.node_id))
			elif op in ('<->'): return BuddyNode(  self._bdd.bdd_biimp(u.node_id, v.node_id))
		elif len(children) == 3 and op == "ite":
			u, v, w = children
			return BuddyNode(  self._bdd.bdd_ite(u.node_id, v.node_id, w.node_id))
		raise Exception(f"operator {op} and children count #{len(children)} do not fit")

	def var(self, x: str) -> "BuddyNode": 
		if x not in self.__name2var_id.keys():
			raise Exception(f"Variable {x} not found!")
		return BuddyNode( self._bdd.bdd_ithvar(self.__name2var_id[x]))

	# --- END ABSTRACT METHODS ---

	def swap_vars(self, v1, v2):
		assert v1 in self.__name2var_id
		assert v2 in self.__name2var_id
		id1, id2 = self.__name2var_id[v1], self.__name2var_id[v2]
		self._bdd.bdd_swapvar(id1, id2)	
		self._bdd.bdd_printorder()

	@property 
	def vars(self) -> tuple[str]:
		return self.__vars

	@property
	def varcount(self) -> int: 
		return len(self.vars)

	@property 
	def nodenum(self) -> int:
		return self._bdd.bdd_getnodenum()

	def __del__(self):
		self._bdd.bdd_done()

	def set_dynamic_reordering(self, type=True):
		if type:
			self._bdd.bdd_autoreorder(3) # sifting as standard reordering
			self._bdd.bdd_enable_reorder()
		else:
			self._bdd.bdd_disable_reorder()

	def reorder(self, method=3):
		rnames = {
			1:"WIN2", 
			2:"WIN2ITE", 
			3:"SIFT", 
			4:"SIFTITE", 
			5:"WIN3", 
			6:"WIN3ITE", 
			7:"RANDOM"}
		print("reorder via",rnames[method])
		# for var in self.vars:
		# 	print(var, self._bdd.bdd_var2level(self.__name2var_id[var]))
		# print("="*10)
		self._bdd.bdd_reorder(method)
		# for var in self.vars:
		# 	print(var, self._bdd.bdd_var2level(self.__name2var_id[var]))

	@classmethod
	def load(file_bdd, vars) -> Tuple["BuddyContext", BuddyNode]:
		# returns new root node of read bdd
		# print(f"load {file_bdd} ...")
		root = c_int()
		buddy = BuddyContext(vars)
		buddy._bdd.bdd_fnload(c_char_p(file_bdd.encode("UTF-8")), byref(root))
		buddy._bdd.bdd_addref(root.value)
		# print(f"loaded {file_bdd}")
		return buddy, BuddyNode(root.value)

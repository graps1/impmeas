import os
from ctypes import CDLL, c_double, c_int, c_char_p, byref, POINTER
from typing import Tuple, Union
from math import comb

from functools import cache

from .repr import Repr, ReprContext

class BuddyNode(Repr):
	def __init__(self, context: "BuddyContext", node_id : int):
		super().__init__(context)
		self.node_id = node_id
		context._bdd.bdd_addref(self.node_id)

	# --- ABSTRACT METHODS ---
	def __hash__(self): 
		return self.node_id.__hash__()

	def cofactor(self, ass: dict[str, bool]) -> "Repr": 
		r = self.ctx.true
		for x in ass:
			xf = self.ctx.var(x)
			if not ass[x]: xf = ~xf
			r = r & xf
		return BuddyNode(self.ctx, self.ctx._bdd.bdd_restrict(self.node_id, r.node_id))

	def flip(self, x : str) -> "BuddyNode":
		xf = self.ctx.var(x)
		f0, f1 = self.cofactor({x: False}), self.cofactor({x: True})
		return xf.ite(f0, f1)	

	def __call__(self, assignment: dict[str, bool]) -> bool: 
		if self == self.ctx.true: return True
		elif self == self.ctx.false: return False
		else:
			sub = self.high if assignment[self.var] else self.low
			return sub(assignment)

	def __copy__(self): 
		return BuddyNode(self.ctx, self.node_id)

	@property
	def vars(self) -> set[str]: 
		return set(v for v,c in self.var_profile.items() if c > 0)

	def satcount(self) -> int: 
		return self.ctx._bdd.bdd_satcount(self.node_id)

	# --- END ABSTRACT METHODS ---

	def ite(self, o1: "BuddyNode", o2: "BuddyNode") -> "BuddyNode": 
		return self.ctx.apply("ite", self, o1, o2)

	def __del__(self):
		if not self.ctx.called_done: 
			self.ctx._bdd.bdd_delref(self.node_id)

	def __eq__(self, other : "BuddyNode"): 
		return isinstance(other, BuddyNode) and self.node_id == other.node_id

	@property
	def var(self) -> str:
		if self.node_id in [0,1]: return None
		return self.ctx.vars[self.ctx._bdd.bdd_var(self.node_id)]

	@property
	def low(self) -> "BuddyNode": 
		return BuddyNode(self.ctx, self.ctx._bdd.bdd_low(self.node_id))

	@property
	def high(self) -> "BuddyNode": 
		return BuddyNode(self.ctx, self.ctx._bdd.bdd_high(self.node_id))

	@property
	def nodecount(self) -> int:
		return self.ctx._bdd.bdd_nodecount(self.node_id)

	@property
	def var_profile(self) -> dict[str, int]:
		# returns a variable-int-dictionary that counts how often variable nodes occur in this function
		profile = self.ctx._bdd.bdd_varprofile(self.node_id)
		return { var: count for var, count in zip(self.ctx.vars, profile.contents ) }
		
	def dump(self, filename="out.bdd"):
		if filename[-3:] == "dot":
			self.ctx._bdd.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), self.node_id)
		if filename[-3:] == "pdf":
			tempf = filename+".tmp"
			self.ctx._bdd.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), self.node_id)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		else:
			self.ctx._bdd.bdd_fnsave(c_char_p(filename.encode("UTF-8")), self.node_id)
			with open(filename+"v", "w") as f:
				f.write("\n".join(self.ctx.vars))

	@property 
	def level(self):
		if self.node_id in [0,1]:
			return len(self.ctx.vars)
		var = self.ctx._bdd.bdd_var(self.node_id)
		return self.ctx._bdd.bdd_var2level(var)

	def wdiff(self, x: str, c = lambda k: 1) -> float:
		if self == self.ctx.true: return c(0)
		elif self == self.ctx.false: return c()

# 	def wcount(self, c = lambda s: 1) -> float:
# 		ell = len(self.ctx.vars) - len(self.vars)
# 		c_ = lambda s: sum(comb(ell, k)*c(s+k) for k in range(ell+1))
# 		return self.__wcount(c=c_)
# 
# 	def __wcount(self, c = lambda s: 1) -> float:
# 		if self == self.ctx.true: return c(0)
# 		elif self == self.ctx.false: return 0
# 		else:
# 			print(self.var)
# 			m0 = len(self.vars) - len(self.low.vars)
# 			c0 = lambda s: sum(comb(m0-1, k)*c(s+k) for k in range(m0))
# 			m1 = len(self.vars) - len(self.high.vars)
# 			c1 = lambda s: sum(comb(m1-1, k)*c(s+k+1) for k in range(m1))
# 			wlow = self.low.__wcount(c=c0)
# 			whigh = self.high.__wcount(c=c1)
# 			return wlow + whigh

class BuddyContext(ReprContext):
	def __init__(self, vars: list[str], lib:str ="/usr/local/lib/libbdd.so") -> None: 
		buddy = CDLL(lib)

		buddy.bdd_varprofile.restype = POINTER(c_int * len(vars))
		buddy.bdd_satcount.restype = c_double
		buddy.bdd_init(1<<28, 1<<20)
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
		self.__called_done = False

	# --- ABSTRACT METHODS ---

	@property
	def false(self) -> BuddyNode:
		return BuddyNode(self, self._bdd.bdd_false())

	@property
	def true(self) -> BuddyNode:
		return BuddyNode(self, self._bdd.bdd_true())

	def apply(self, op : str, *children) -> BuddyNode:
		if op in ('~'):
			u, = children
			return BuddyNode(self,  self._bdd.bdd_not(u.node_id))
		elif len(children)==2:
			u, v = children
			if op in ('|'): return BuddyNode(self,  self._bdd.bdd_or(u.node_id, v.node_id))
			elif op in ('&'): return BuddyNode(self,  self._bdd.bdd_and(u.node_id, v.node_id))
			elif op in ('^'): return BuddyNode(self,  self._bdd.bdd_xor(u.node_id, v.node_id))
			elif op in ('->'): return BuddyNode(self,  self._bdd.bdd_imp(u.node_id, v.node_id))
			elif op in ('<->'): return BuddyNode(self,  self._bdd.bdd_biimp(u.node_id, v.node_id))
		elif len(children) == 3 and op == "ite":
			u, v, w = children
			return BuddyNode(self,  self._bdd.bdd_ite(u.node_id, v.node_id, w.node_id))
		raise Exception(f"operator {op} and children count #{len(children)} do not fit")

	def var(self, x: str) -> "BuddyNode": 
		if x not in self.__name2var_id.keys():
			raise Exception(f"Variable {x} not found!")
		return BuddyNode(self, self._bdd.bdd_ithvar(self.__name2var_id[x]))

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
	def called_done(self) -> bool:
		return self.__called_done

	@property
	def varcount(self) -> int: 
		return len(self.vars)

	@property 
	def nodenum(self) -> int:
		return self._bdd.bdd_getnodenum()

	def __enter__(self): 
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback): 
		self._bdd.bdd_done()
		self.__called_done =True

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
		return buddy, BuddyNode(buddy, root.value)

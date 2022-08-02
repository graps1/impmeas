import ast 
import os
from ctypes import CDLL, c_double, c_int, c_char_p, byref

class BuddyFunc:
	def __init__(self, model : "Buddy", node : int):
		self.node = node
		self.model = model 

	def __hash__(self): return self.node

	def __call_op(self, op, *others):
		others = list(others)
		for idx in range(len(others)):
			# if they're already integers (ie node ids) then don't do anything
			if isinstance(others[idx], BuddyFunc):
				others[idx] = others[idx].node
		return BuddyFunc(self.model, self.model._apply(op, self.node, *others))

	def __and__(self, other): return self.__call_op("&", other)
	def __or__(self, other): return self.__call_op("|", other)
	def __xor__(self, other): return self.__call_op("^", other)
	def __geq__(self, other): return other <= self
	def __leq__(self, other): return self.__call_op("->", other)
	def __eq__(self, other): return self.__call_op("<->", other)
	def __invert__(self): return self.__call_op("~")
	def ite(self, if_true, if_false): return self.__call_op("ite", if_true, if_false)

	@property
	def var(self):
		if self.node in [0,1]: return None
		return BuddyFunc(self.model, self.model._bdd.bdd_ithvar(self.model._bdd.bdd_var(self.node)))
	@property
	def low(self): return BuddyFunc(self.model, self.model._bdd.bdd_low(self.node))
	@property
	def high(self): return BuddyFunc(self.model, self.model._bdd.bdd_high(self.node))
	@property
	def level(self): return self.model._bdd.bdd_level(self.node)
	@property
	def get_size(self): return self.model._bdd.bdd_nodecount(self.node)
	@property
	def count(self): return self.model._bdd.bdd_satcount(self.node)
	@property
	def support(self): return self.model._bdd.bdd_support(self.node)

	def restrict(self, u : "BuddyFunc"):
		# x = self.var(x) if val else self.nvar(x)
		return BuddyFunc(self.model, self.model._bdd.bdd_restrict(self.node, u.node))

	### reference counting and garbage
	def incref(self): return self.model._bdd.bdd_addref(self.node)
	def decref(self): return self.model._bdd.bdd_delref(self.node)

	def dump(self, filename="out.bdd"):
		tempf = filename+".tmp"
		if filename[-3:] == "dot":
			self.model._bdd.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), self.node)
		if filename[-3:] == "pdf":
			self.model._bdd.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), self.node)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		# else:
		# 	self.model._bdd.bdd_fnsave(c_char_p(filename.encode("UTF-8")), self.node)
		# 	with open(filename+"v", "w") as f:
		# 		for i in range(len(self.var_dict)):
		# 			f.write(f"{self.var_dict[i]}\n")
		# 		f.close()

class Buddy:
	def __init__(self, vars: list, lib="/usr/local/lib/libbdd.so") -> None: 
		buddy = CDLL(lib)

		buddy.bdd_satcount.restype = c_double
		buddy.bdd_init(1<<26, 1<<20)
		buddy.bdd_setmaxincrease(1<<27)
		buddy.bdd_setcacheratio(32)
		buddy.bdd_setvarnum(c_int(len(vars)))
		self._bdd = buddy

		# generate dict for varnames
		self.vars = vars
		self.name2node = { x : k for k, x in enumerate(self.vars) }

	@property
	def varcount(self) -> int: return len(self.vars)

	# parses a formula according to python's internal parser
	# this is probably the easiest way to add support for formulas...
	def parse(self, formula : str) -> BuddyFunc:
		def rec(node):
			if isinstance(node, ast.Name):
				if node.id not in self.name2node.keys():
					raise Exception(f"Variable {node.id} not found!")
				return self._bdd.bdd_ithvar(self.name2node[node.id])
			elif isinstance(node, ast.Module):
				return rec(node.body[0])
			elif isinstance(node, ast.Expr):
				return rec(node.value)
			elif isinstance(node, ast.BinOp) and type(node.op) in { ast.BitOr, ast.BitXor, ast.BitAnd }:
				op = { 
					ast.BitOr: "|",
					ast.BitXor: "^",
					ast.BitAnd: "&" }[type(node.op)]
				return self._apply(op, rec(node.left), rec(node.right))
			elif isinstance(node, ast.UnaryOp) and type(node.op) in { ast.Invert, ast.Not }:
				return self._apply("~", node.operand)
			else:
				raise Exception(f"Node {node} of unknown type!")
		return BuddyFunc(self, rec(ast.parse(formula)))

	def __enter__(self): return self
	def __exit__(self, exc_type, exc_value, exc_traceback): self._bdd.bdd_done()

	def set_dynamic_reordering(self, type=True):
		if type:
			self._bdd.bdd_autoreorder(3) # sifting as standard reordering
			self._bdd.bdd_enable_reorder()
		else:
			self._bdd.bdd_disable_reorder()

	@property
	def false(self):
		return BuddyFunc(self, self._bdd.bdd_false())

	@property
	def true(self):
		return BuddyFunc(self, self._bdd.bdd_true())

	def _apply(self, op : str, u : int, v : int = None, w : int = None) -> int:
		if op in ('~', 'not', '!'):
			return self._bdd.bdd_not(u)
		elif op in ('or', r'\/', '|', '||'):
			return self._bdd.bdd_or(u, v)
		elif op in ('and', '/\\', '&', '&&', "band", "*", "land", "."):
			return self._bdd.bdd_and(u, v)
		elif op in ('xor', '^'):
			return self._bdd.bdd_xor(u, v)
		elif op in ('=>', '->', 'implies'):
			return self._bdd.bdd_imp(u, v)
		elif op in ('<=>', '<->', 'equiv'):
			return self._bdd.bdd_biimp(u, v)
		elif op in ('diff', '-'):
			return self._bdd.bdd_ite(u, self._bdd.bdd_not(u), self.false.node)
		elif op == 'ite':
			return self._bdd.bdd_ite(u, v, w)
		else:
			raise Exception(f'unknown operator "{op}"')

	def add_reorder_vars(self):
		self._bdd.bdd_varblockall()

	def reorder(self, method=3):
		rnames = {1:"WIN2", 2:"WIN2ITE", 3:"SIFT", 4:"SIFTITE", 5:"WIN3", 6:"WIN3ITE"}
		print("reorder via",rnames[method])
		self._bdd.bdd_reorder(method)

	def load(self, filename="in.bdd"):
		# returns new root node of read bdd
		print(f"load {filename} ...")
		root = c_int()
		self._bdd.bdd_fnload(c_char_p(filename.encode("UTF-8")), byref(root))
		self.incref(root.value)
		print(f"loaded {filename}")
		return root.value

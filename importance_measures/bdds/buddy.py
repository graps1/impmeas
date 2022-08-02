import ast 
import os
from ctypes import CDLL, c_double, c_int, c_char_p, byref

class BuDDy:

	def __init__(self, var_order: list, lib="/usr/local/lib/libbdd.so"): 
		buddy = CDLL(lib)

		buddy.bdd_satcountln.restype = c_double

		buddy.bdd_init(1<<26, 1<<20)
		buddy.bdd_setmaxincrease(1<<27)
		buddy.bdd_setcacheratio(32)
		buddy.bdd_setvarnum(c_int(len(var_order)))

		# generate dict for varnames
		self.var_dict = dict(enumerate(var_order))
		self.name_dict = { x : k for k, x in self.var_dict.items() }

		self._bdd = buddy

	# parses a formula according to python's internal parser
	# this is probably the easiest way to add support for formulas...
	def parse(self, formula):
		def rec(node):
			if isinstance(node, ast.Name):
				return self.var(node.id)
			elif isinstance(node, ast.Module):
				return rec(node.body[0])
			elif isinstance(node, ast.Expr):
				return rec(node.value)
			elif isinstance(node, ast.BinOp) and type(node.op) in { ast.BitOr, ast.BitXor, ast.BitAnd }:
				op = { ast.BitOr: "|", ast.BitXor: "^", ast.BitAnd: "&" }[type(node.op)]
				return self.apply(op, rec(node.left), rec(node.right))
			elif isinstance(node, ast.UnaryOp) and type(node.op) in { ast.Invert, ast.Not }:
				return self.apply("~", rec(node.operand))
			else:
				raise Exception(f"Node {node} of unknown type!")
		return rec(ast.parse(formula))
	
	def __del__(self):
		self._bdd.bdd_done()

	def set_dynamic_reordering(self, type=True):
		if type:
			self._bdd.bdd_autoreorder(3) # sifting as standard reordering
			self._bdd.bdd_enable_reorder()
		else:
			self._bdd.bdd_disable_reorder()

	### Basic methods
	@property
	def false(self):
		return self._bdd.bdd_false()

	@property
	def true(self):
		return self._bdd.bdd_true()

	def top_level_var(self, f):
		if f in [0,1]:
			return None
		return self._bdd.bdd_ithvar(self._bdd.bdd_var(f))

	def var(self, x):
		if x not in self.name_dict.keys():
			print(f"variable {x} not found!")
		return self._bdd.bdd_ithvar(self.name_dict[x])

	def nvar(self, x):
		if x not in self.name_dict.keys():
			print(f"variable {x} not found!")
		return self._bdd.bdd_nithvar(self.name_dict[x])

	def low(self, u):
		return self._bdd.bdd_low(u)

	def high(self, u):
		return self._bdd.bdd_high(u)

	def level(self, u):
		return self._bdd.bdd_level(u)

	def get_size(self, u):
		return self._bdd.bdd_nodecount(u)

	def lncount(self, u):
		return self._bdd.bdd_satcountln(u)

	def support(self, u):
		return self._bdd.bdd_support(u)
	
	def ite(self, u, v, w):
		return self._bdd.bdd_ite(u,v,w)

	def apply(self, op, u, v = None, w = None):
		if op in ('~', 'not', '!'):
			return self._bdd.bdd_not(u)
		elif op in ('or', r'\/', '|', '||'):
			return self._bdd.bdd_or(u, v)
		elif op in ('and', '/\\', '&', '&&'):
			return self._bdd.bdd_and(u, v)
		elif op in ('band', '*'):
			return self._bdd.bdd_and(u, v)
		elif op in ('land', '.'):
			return self._bdd.bdd_and(u, v)
		elif op in ('xor', '^'):
			return self._bdd.bdd_xor(u, v)
		elif op in ('=>', '->', 'implies'):
			return self._bdd.bdd_imp(u, v)
		elif op in ('<=>', '<->', 'equiv'):
			return self._bdd.bdd_biimp(u, v)
		elif op in ('diff', '-'):
			return self.ite(u, self._bdd.bdd_not(u), self.false)
		elif op == 'ite':
			return self.ite(u, v, w)
		else:
			raise Exception(f'unknown operator "{op}"')

	def neg(self, u):
		return self._bdd.bdd_not(u)

	def add_reorder_vars(self):
		self._bdd.bdd_varblockall()

	def reorder(self, varorder = None, method=3):
		rnames = {1:"WIN2", 2:"WIN2ITE", 3:"SIFT", 4:"SIFTITE", 5:"WIN3", 6:"WIN3ITE"}
		print("reorder via",rnames[method])
		self._bdd.bdd_reorder(method)

	### reference counting and garbage
	def incref(self, u):
		return self._bdd.bdd_addref(u)

	def decref(self, u):
		return self._bdd.bdd_delref(u)

	def dump(self, u=None, filename="out.bdd"):
		print(f"dump {filename} ...", end="")
		tempf = filename+".tmp"
		if filename[-3:] == "dot":
			self._bdd.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), u)
		if filename[-3:] == "pdf":
			self._bdd.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), u)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		else:
			self._bdd.bdd_fnsave(c_char_p(filename.encode("UTF-8")), u)
			with open(filename+"v", "w") as f:
				for i in range(len(self.var_dict)):
					f.write(f"{self.var_dict[i]}\n")
				f.close()
		print("done")

	def load(self, filename="in.bdd"):
		# returns new root node of read bdd
		print(f"load {filename} ...")
		root = c_int()
		self._bdd.bdd_fnload(c_char_p(filename.encode("UTF-8")), byref(root))
		self.incref(root.value)
		print(f"loaded {filename}")
		return root.value

	def restrict_var_to_val(self, f, x, val):
		x = self.var(x) if val else self.nvar(x)
		return self._bdd.bdd_restrict(f, x)

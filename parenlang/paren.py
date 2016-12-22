import attr

from .util import auto_assign # Assigns its arguments to instance attributes

@attr.s(frozen=True, hash=False)
class Paren:
	filename        	= attr.ib(default='', cmp=False)
	start           	= attr.ib(default=None, cmp=False)
	end             	= attr.ib(default=None, cmp=False)
	start_annotation	= attr.ib(default='', cmp=False)
	end_annotation  	= attr.ib(default='', cmp=False)
	children        	= attr.ib(default=attr.Factory(tuple))
	# _hash         	= attr.ib(init=False, cmp=False, hash=False)

	def add_child(self, paren):
		return Paren(
			self.filename,
			self.start,
			self.end,
			self.start_annotation,
			self.end_annotation,
			self.children + (paren,)
		)

	def bintree_form(self):
		children = tuple(map(Paren.bintree_form, self.children))
		if len(children) > 2:
			group = attr.assoc(self, children=children[:-1])
			children = (group, children[-1])
		return attr.assoc(self, children=children)

	def shorthand_form(self):
		children = tuple(map(Paren.shorthand_form, self.children))
		if len(children) > 1 and len(children[0].children) > 1:
			children = children[0].children + children[1:]
		return attr.assoc(self, children=children)

	def binary_repr(self):
		if len(self.children) == 0:
			return '1'
		elif len(self.children) == 1:
			child_repr = self.children[0].binary_repr()
			out = child_repr + '0' * len(child_repr)
			return out
		elif len(self.children) == 2:
			bintree_form = self
		else:
			bintree_form = self.bintree_form()

		# len(bintree_form.children) == 2
		left_repr = bintree_form.children[0].binary_repr()
		right_repr = bintree_form.children[1].binary_repr()
		diff = len(left_repr) - len(right_repr)
		if diff < 0:
			left_repr = '0'*(-diff) + left_repr
		elif diff > 0:
			right_repr = '0'*diff + right_repr
		return left_repr + right_repr

	def succinct_repr(self):
		if len(self.children) == 0:
			return '100'
		elif len(self.children) == 1:
			left_repr = self.children[0].succinct_repr()
			return '1' + left_repr + '0'
		elif len(self.children) == 2:
			bintree_form = self
		else:
			bintree_form = self.bintree_form()
		left_repr = bintree_form.children[0].succinct_repr()
		right_repr = bintree_form.children[1].succinct_repr()
		out = '1' + left_repr + right_repr
		return out


	def __hash__(self):
		return hash(self.children)

	def __str__(self):
		return '(' + ''.join(map(str, self.children)) + ')'

class Paren_old:
	"""
	A paren expression.

	Examples of parens:
	(): Paren([]) # The empty paren
	(()): Paren([Paren([])]) # A paren containing one element, the empty paren
	(()()): Paren([Paren([]), Paren([])]) # A paren containing two elements, each being the empty paren

	(I think you get the (point)): Paren([Paren([])]) # Yeah ok I'll stop now

	In addition to storing the tree structure of parens, there are additional
	data completely ignored by the VM but we store to allow nice parsing error
	messages and defining structure using annotations which could allow compile
	time warnings.

	file is a string containing the filename this paren is in.
	start is a line,col tuple containing the position of the opening paren.
	end is a line,col tuple containing the position of the closing paren.
	start_annotation is the string preceding the opening paren.
	end_annotation is the string preceding the closing paren.

	'annotate()': Paren([], start_annotation='annotate')
	'annotate(()strange())': Paren([Paren([]), Paren([], start_annotation='strange')], start_annotation='annotate')
	'(end annotations)': Paren([], end_annotation='end annotations')
	"""
	@auto_assign
	def __init__(self, filename='', start=None, end=None, start_annotation='', end_annotation='', children=None, parent=None):
		if children == None:
			self.children = []

	def add_child(self, paren):
		self.children.append(paren)

	def start_paren(self, line, col, start_annotation, parent):
		self.start = (line, col)
		self.start_annotation = start_annotation
		self.parent = parent

	def end_paren(self, line, col, end_annotation):
		self.end = (line, col)
		self.end_annotation = end_annotation

	def bintree_form(self):
		out = Paren(self.filename, self.start, self.end, self.start_annotation, self.end_annotation, None, self.parent)
		out.children = list(map(Paren.bintree_form, self.children))
		if len(self.children) > 2:
			group = Paren(out.filename, out.start, out.end, out.start_annotation, out.end_annotation, out.children[:-1], out)
			group = group.bintree_form()
			out.children = [group, out.children[-1]]
		return out

	def shorthand_form(self):
		out = Paren(self.filename, self.start, self.end, self.start_annotation, self.end_annotation, None, self.parent)
		out.children = list(map(Paren.shorthand_form, self.children))
		if len(out.children) > 1 and len(out.children[0].children) > 1:
			out.children = out.children[0].children + out.children[1:]
		return out

	def binary_repr(self):
		if len(self.children) == 0:
			return '1'
		elif len(self.children) == 1:
			child_repr = self.children[0].binary_repr()
			out = child_repr + '0' * len(child_repr)
			return out
		elif len(self.children) == 2:
			bintree_form = self
		else:
			bintree_form = self.bintree_form()

		# len(bintree_form.children) == 2
		left_repr = bintree_form.children[0].binary_repr()
		right_repr = bintree_form.children[1].binary_repr()
		diff = len(left_repr) - len(right_repr)
		if diff < 0:
			left_repr = '0'*(-diff) + left_repr
		elif diff > 0:
			right_repr = '0'*diff + right_repr
		return left_repr + right_repr

	def __hash__(self):
		# # This one sucks... so many collisions!
		# if len(self.children) == 0:
		#	return 373588441
		# h = 1
		# for c in self.children:
		#	h *= 9223372036854775807
		#	h += hash(c) * 32416189261 + 179425943
		#	h %= 18446744073709551557
		# return h

		# This one does not collide for all 16 bit parens, however it has to
		# convert to str and hash the string. This is not ideal.
		# if len(self.children) == 0:
		#	return 1
		# h = 0
		# for c in self.children:
		#	hc = hash(c)
		#	# hhc = hash(str(hc)) # Here
		#	hhc = (hc * 790307613855488863 + 4011653645208336749) & 0xFFFFFFFFFFFFFFFF
		#	h ^= hhc
		#	h = ((h<<63) | (h>>1)) & 0xFFFFFFFFFFFFFFFFF
		# return h

		return hash(tuple(self.children))

	def __eq__(self, other):
		if len(self.children) != len(other.children):
			return False
		for i in range(len(self.children)):
			if self.children[i] != other.children[i]:
				return False
		return True

	def __str__(self):
		return '(' + ''.join(map(str, self.children)) + ')'

	def __repr__(self):
		return	(	'Paren(filename={}, start={}, end={}, '
		      	 	'start_annotation={}, end_annotation={}, children={})'.format(
		      	 	repr(self.filename), repr(self.start), repr(self.end),
		      	 	repr(self.start_annotation), repr(self.end_annotation),
		      	 	repr(self.children)))

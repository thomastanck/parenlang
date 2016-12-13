import re

from .util import auto_assign # Assigns its arguments to instance attributes

class Paren:
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

	def __str__(self):
		return '(' + ''.join(map(str, self.children)) + ')'

	def __repr__(self):
		return	(	'Paren(filename={}, start={}, end={}, '
		      	 	'start_annotation={}, end_annotation={}, children={})'.format(
		      	 	repr(self.filename), repr(self.start), repr(self.end),
		      	 	repr(self.start_annotation), repr(self.end_annotation),
		      	 	repr(self.children)))

class BinaryReprParser:
	"""
	In comes binary representation (in string form)
	Out goes parse tree (a Paren)
	"""
	@auto_assign
	def __init__(self, instr):
		pass

	def parse(self):
		_, paren = BinaryReprParser.from_binary_repr(self.instr)
		return paren

	@staticmethod
	def is_zero(binary_repr):
		for c in binary_repr:
			if c == '1':
				return False
		return True

	@staticmethod
	def from_binary_repr(binary_repr):
		if len(binary_repr) == 1:
			if binary_repr == '1':
				return 0, Paren()
			else:
				raise Exception

		assert (len(binary_repr) % 2) == 0
		left_repr = binary_repr[:len(binary_repr) // 2]
		right_repr = binary_repr[len(binary_repr) // 2:]
		if BinaryReprParser.is_zero(left_repr):
			# Left-padded to make up for difference in depth
			depth, out = BinaryReprParser.from_binary_repr(right_repr)
		elif BinaryReprParser.is_zero(right_repr):
			# Right-padded because there is no right branch
			left_depth, left_paren = BinaryReprParser.from_binary_repr(left_repr)
			out = Paren()
			out.children.append(left_paren)
			depth = left_depth + 1
			assert len(binary_repr) == (2**depth)
		else:
			# Neither left or right padded, both branches exist
			left_depth, left_paren = BinaryReprParser.from_binary_repr(left_repr)
			right_depth, right_paren = BinaryReprParser.from_binary_repr(right_repr)
			out = Paren()
			out.children.append(left_paren)
			out.children.append(right_paren)
			depth = max(left_depth, right_depth) + 1
			assert len(binary_repr) == (2**depth)
		return depth, out

class Parser:
	"""
	In comes string
	Out goes parse tree (a Paren)
	"""
	def __init__(self, instr, filename='<nil>'):
		self.filename = filename
		self.instr = instr # input string
		self.reset_parse_state()

	def reset_parse_state(self):
		self.remaining = self.instr # String that's not yet parsed
		self.lines = [] # List of lines that have been parsed
		self.curlinepos = 0 # The position of the current line
		self.line = 1 # Current line number
		self.col = 1 # Current column number
		self.out = [] # Output parens

	def parse(self):
		"""
		Parses into a list of lists of lists...
		"""
		self.reset_parse_state()
		while len(self.remaining) > 0:
			parsed = self.parse_paren()
			if parsed != None:
				self.out.append(parsed)
		return self.out

	def parse_paren(self, parentparen=None):
		"""
		Recursive part of the parser.
		Returns the processed paren (list of lists of lists...).
		"""
		paren = Paren(self.filename)

		start_annotation, tok = self.eat()
		if tok == None:
			return None

		if tok != '(': # assert(tok == '(')
			self.unexpected_closing_error()

		paren.start_paren(self.line, self.col-1, start_annotation, parentparen)

		while len(self.remaining) > 0:
			annotation, tok = self.peek()
			if tok == '(':
				parsed = self.parse_paren(paren)
				paren.add_child(parsed)
			elif tok == ')':
				self.eat() # Advance the position
				paren.end_paren(self.line, self.col-1, annotation)
				# TOOD: Run linter here! (to check if start and end annotations
				# match for example)
				return paren
			else:
				break
		self.eat() # just to advance it to the actual EOF
		self.unexpected_eof_error(paren)

	def eat(self):
		"""
		Returns the next token.
		Also removes the token from the remaining string so the next token can
		be parsed.
		"""
		annotation, tok = self.peek()
		# Change line and col numbers, consume remaining
		for c in annotation:
			if c == '\n':
				self.line += 1
				self.lines.append(self.instr[self.curlinepos : self.curlinepos+self.col-1])
				self.curlinepos += self.col
				self.col = 1
				continue
			self.col += 1
		self.remaining = self.remaining[len(annotation)+1:]
		self.col += 1 if tok != None else 0
		return annotation, tok

	def peek(self):
		"""
		Returns the next token.

		# Also advances the current position up to the token (so that
		# self.remaining[0] contains the token)
		"""
		for i, c in enumerate(self.remaining):
			if c in ['(', ')']:
				return self.remaining[:i], c
		return self.remaining, None

	def get_current_line(self):
		newlinepos = self.instr[self.curlinepos:].find('\n')
		if newlinepos == -1:
			return self.instr[self.curlinepos:]
		else:
			return self.instr[self.curlinepos:self.curlinepos+newlinepos]

	def unexpected_closing_error(self):
		prefix = '{}:{}:{}:'.format(self.filename, self.line, self.col-1)
		print('{} error: Expected ( but got ) instead.'.format(prefix))
		print('{}  hint: Did you forget to remove a closing paren?'.format(' '*len(prefix)))
		self.print_line_error((self.line, self.col-1))

		if len(self.out) > 0:
			print('{}  note: Previous paren starts here'.format(' '*len(prefix)))
			prevparen = self.out[-1]
			self.print_line_error(prevparen.start, (prevparen.end[0], prevparen.end[1]+1))

		print()
		raise SyntaxError('{} Unexpected closing paren'.format(prefix))

	def unexpected_eof_error(self, paren):
		prefix = '{}:{}:{}:'.format(self.filename, self.line, self.col)
		print('{} error: Unexpected EOF'.format(prefix))
		print('{}  hint: Did you forget to close a paren?'.format(' '*len(prefix)))
		self.print_line_error((self.line, self.col), note=' EOF')

		num_unclosed = 0
		unclosed = paren
		while unclosed:
			unclosed = unclosed.parent
			num_unclosed += 1

		print('{}  note: There are {} unclosed parens'.format(' '*len(prefix), num_unclosed))
		unclosed = paren
		while unclosed:
			prefix = '{}:{}:{}:'.format(unclosed.filename, unclosed.start[0], unclosed.start[1])
			print('{}  note: unclosed paren'.format(prefix))
			self.print_line_error(unclosed.start, (self.line, self.col))
			unclosed = unclosed.parent

		print()
		raise SyntaxError('{} Unexpected EOF'.format(prefix))

	def print_line_error(self, start, end=None, note=''):
		startline, startcol = start
		# Print the actual line
		print(self.get_line(startline))
		# Print the arrow
		if end == None:
			# Arrow has no extension
			print(' '*(startcol-1) + '^' + note)
			return
		endline, endcol = end
		if endline > startline:
			# Arrow extends to end of line
			print(' '*(startcol-1) + '^' + '~'*(len(self.lines[startline-1])-startcol) + note)
		elif endline < startline:
			# Arrow extends to start of line
			print('~'*(startcol-1) + '^' + note)
		else:
			# Arrow extends to another point on the same line
			if endcol > startcol:
				# Arrow extends to the right
				print(' '*(startcol-1) + '^' + '~'*(endcol-startcol-1) + note)
			elif endcol < startcol:
				# Arrow extends to the left
				print(' '*(endcol) + '~'*(startcol-endcol-1) + '^' + note)
			else:
				# Arrow has no extension
				print(' '*(startcol-1) + '^' + note)

	def get_line(self, line):
		if line-1 < len(self.lines):
			return self.lines[line-1]
		elif line-1 == len(self.lines):
			return self.get_current_line()
		else:
			raise RuntimeError("Tried to get line that hasn't been parsed")

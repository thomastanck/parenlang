from .paren import Paren
from .util import auto_assign # Assigns its arguments to instance attributes

class SuccinctReprParser:
	def __init__(self):
		pass

	def parse(self, instr):
		c, instr = instr[0], instr[1:]
		if c == '0':
			return None, instr
		# c == '1'
		left, instr = self.parse(instr)
		right, instr = self.parse(instr)
		if left == None:
			return Paren(), instr
		elif right == None:
			return Paren(children=(left,)), instr
		else:
			return Paren(children=(left, right)), instr

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
			out = Paren(children=(left_paren,))
			depth = left_depth + 1
			assert len(binary_repr) == (2**depth)
		else:
			# Neither left or right padded, both branches exist
			left_depth, left_paren = BinaryReprParser.from_binary_repr(left_repr)
			right_depth, right_paren = BinaryReprParser.from_binary_repr(right_repr)
			out = Paren(children=(left_paren, right_paren))
			depth = max(left_depth, right_depth) + 1
			assert len(binary_repr) == (2**depth)
		return depth, out


class RecursiveParser:
	"""
	In comes string
	Out goes parse tree (a Paren)
	"""
	def __init__(self, filename='<nil>'):
		self.filename = filename
		self.instr = ''
		self.reset_parse_state()

	def reset_parse_state(self):
		self.remaining = self.instr # String that's not yet parsed
		self.lines = [] # List of lines that have been parsed
		self.curlinepos = 0 # The position of the current line
		self.line = 1 # Current line number
		self.col = 1 # Current column number
		self.out = [] # Output parens

	def parse(self, instr):
		"""
		Parses into a list of lists of lists...
		"""
		self.instr = instr
		self.reset_parse_state()
		while len(self.remaining) > 0:
			parsed = self.parse_paren()
			if parsed is not None:
				self.out.append(parsed)
		return self.out

	def parse_paren(self):
		"""
		Recursive part of the parser.
		Returns the processed paren (list of lists of lists...).
		"""
		# paren = Paren(self.filename)
		children = []

		start_annotation, tok = self.eat()
		if tok == None:
			return None

		if tok != '(': # assert(tok == '(')
			self.unexpected_closing_error()

		start = (self.line, self.col-1)
		# paren.start_paren(self.line, self.col-1, start_annotation, parentparen)

		while len(self.remaining) > 0:
			annotation, tok = self.peek()
			if tok == '(':
				parsed = self.parse_paren()
				children.append(parsed)
				# paren.add_child(parsed)
			elif tok == ')':
				self.eat() # Advance the position
				# paren.end_paren(self.line, self.col-1, annotation)
				end = (self.line, self.col-1)
				paren = Paren(self.filename, start, end, start_annotation, annotation, tuple(children))
				# TOOD: Run linter here! (to check if start and end annotations
				# match for example)
				return paren
			else:
				break
		self.eat() # just to advance it to the actual EOF
		paren = Paren(self.filename, start, None, start_annotation, '', tuple(children))
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

		# num_unclosed = 0
		# unclosed = paren
		# while unclosed:
		#	unclosed = unclosed.parent
		#	num_unclosed += 1

		# print('{}  note: There are {} unclosed parens'.format(' '*len(prefix), num_unclosed))
		# unclosed = paren
		# while unclosed:
		#	prefix = '{}:{}:{}:'.format(unclosed.filename, unclosed.start[0], unclosed.start[1])
		#	print('{}  note: unclosed paren'.format(prefix))
		#	self.print_line_error(unclosed.start, (self.line, self.col))
		#	unclosed = unclosed.parent

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


class FlatParser:
	"""
	In comes string
	Out goes parse tree (a list of Paren)
	"""
	def __init__(self, filename='<nil>'):
		self.filename = filename
		self.instr = '' # input string
		self.reset_parse_state()

	def reset_parse_state(self):
		self.remaining = self.instr # String that's not yet parsed
		self.lines = [] # List of lines that have been parsed
		self.curlinepos = 0 # The position of the current line
		self.line = 1 # Current line number
		self.col = 1 # Current column number

		self.current_annotation = ''
		self.paren_list_stack = [[]]
		self.opening_pos_stack = []
		self.num_out = 0

	def parse(self, instr):
		self.parse_bit(instr)
		return self.collect()

	def parse_bit(self, instr):
		self.instr += instr
		for c in instr:
			pos = (self.line, self.col)
			# Parse if paren
			if c == '(':
				self.paren_list_stack.append([])
				self.opening_pos_stack.append((self.current_annotation, (self.line, self.col)))
				self.current_annotation = ''
			elif c == ')':
				if len(self.opening_pos_stack) == 0:
					self.unexpected_closing_error(pos)
				start_annotation, start_pos = self.opening_pos_stack.pop()
				children = tuple(self.paren_list_stack.pop())
				p = Paren(self.filename, start_pos, pos, start_annotation, self.current_annotation, children)
				self.paren_list_stack[-1].append(p)
				self.current_annotation = ''
			else:
				self.current_annotation += c

			# Set position variables
			if c == '\n':
				self.lines.append(self.instr[self.curlinepos:self.curlinepos+self.col-1])
				self.curlinepos += self.col
				self.line += 1
				self.col = 1
			else:
				self.col += 1

		return self

	def collect(self):
		if len(self.opening_pos_stack) > 0:
			self.unexpected_eof_error((self.line, self.col))
		return self.paren_list_stack[0]

	def get_current_line(self):
		newlinepos = self.instr[self.curlinepos:].find('\n')
		if newlinepos == -1:
			return self.instr[self.curlinepos:]
		else:
			return self.instr[self.curlinepos:self.curlinepos+newlinepos]

	def unexpected_closing_error(self, pos):
		line, col = pos
		prefix = '{}:{}:{}:'.format(self.filename, line, col-1)
		print('{} error: Expected ( but got ) instead.'.format(prefix))
		print('{}  hint: Did you forget to remove a closing paren?'.format(' '*len(prefix)))
		self.print_line_error((line, col-1))

		if len(self.paren_list_stack[0]) > 0:
			print('{}  note: Previous paren starts here'.format(' '*len(prefix)))
			prevparen = self.paren_list_stack[0][-1]
			self.print_line_error(prevparen.start, (prevparen.end[0], prevparen.end[1]+1))

		print()
		raise SyntaxError('{} Unexpected closing paren'.format(prefix))

	def unexpected_eof_error(self, pos):
		line, col = pos
		prefix = '{}:{}:{}:'.format(self.filename, line, col)
		print('{} error: Unexpected EOF'.format(prefix))
		print('{}  hint: Did you forget to close a paren?'.format(' '*len(prefix)))
		self.print_line_error((line, col), note=' EOF')

		print('{}  note: There are {} unclosed parens'.format(' '*len(prefix), len(self.opening_pos_stack)))
		for (annotation, unclosed_pos) in self.opening_pos_stack:
			prefix = '{}:{}:{}:'.format(self.filename, unclosed_pos[0], unclosed_pos[1])
			print('{}  note: unclosed paren'.format(prefix))
			self.print_line_error(unclosed_pos, pos)

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


Parser = FlatParser


###################################################
# vvvv DON'T USE! THIS WAS JUST MADE FOR FUN vvvv #
###################################################

class GeneratorBasedParser:
	"""
	Call parse with string
	Call end for EOF, or call parse with FlatParser.EOF
	Call collect to end parsing and retrieve parse tree (a list of Paren)
	"""
	class EOF: pass

	def __init__(self, filename='<nil>'):
		self.filename = filename
		self.instr = ''

		self.curlinepos = 0
		self.lines = []

		self.opening_stack = []
		self.paren_list_stack = [[]]

		self.parsing = True

		self.tokenizer = self.tokenizer_func()
		self.tokenizer.send(None)
		self.parser = self.parser_func()
		self.parser.send(None)

	def parse(self, instr):
		if instr is not FlatParser.EOF:
			self.instr += instr
		self.tokenizer.send(instr)
		return self

	def end(self):
		if self.parsing:
			self.parse(FlatParser.EOF)
		return self
	def collect(self):
		if self.parsing:
			self.parse(FlatParser.EOF)

		return self.paren_list_stack[0]

	def tokenizer_func(self):
		line = 1
		col = 1
		annotation = ''

		while True:
			a = yield
			if a == FlatParser.EOF:
				self.parser.send((a, annotation, (line, col)))
				self.parsing = False
				break
			for c in a:
				if c == '(' or c == ')':
					self.parser.send((c, annotation, (line, col)))
					annotation = ''
				else:
					annotation += c
				if c == '\n':
					self.lines.append(self.instr[self.curlinepos : self.curlinepos+col-1])
					self.curlinepos += col
					line += 1
					col = 1
				else:
					col += 1
		yield None

	def parser_func(self):
		while True:
			token = yield
			tok, annotation, pos = token
			if tok == FlatParser.EOF:
				if len(self.opening_stack) > 0:
					self.unexpected_eof_error(pos)
				break
			elif tok == '(':
				self.opening_stack.append(token)
				self.paren_list_stack.append([])
			elif tok == ')':
				if len(self.opening_stack) == 0:
					self.unexpected_closing_error(pos)
				opening_token = self.opening_stack.pop()
				_, start_annotation, start_pos = opening_token
				paren_list = self.paren_list_stack.pop()
				p = Paren(self.filename, start_pos, pos, start_annotation, annotation, tuple(paren_list))
				self.paren_list_stack[-1].append(p)
			else:
				raise RuntimeError('Illegal token (please inform the maintainer that this occurred!)')
		yield None

	def get_current_line(self):
		newlinepos = self.instr[self.curlinepos:].find('\n')
		if newlinepos == -1:
			return self.instr[self.curlinepos:]
		else:
			return self.instr[self.curlinepos:self.curlinepos+newlinepos]

	def unexpected_closing_error(self, pos):
		line, col = pos
		prefix = '{}:{}:{}:'.format(self.filename, line, col-1)
		print('{} error: Expected ( but got ) instead.'.format(prefix))
		print('{}  hint: Did you forget to remove a closing paren?'.format(' '*len(prefix)))
		self.print_line_error((line, col-1))

		if len(self.out) > 0:
			print('{}  note: Previous paren starts here'.format(' '*len(prefix)))
			prevparen = self.out[-1]
			self.print_line_error(prevparen.start, (prevparen.end[0], prevparen.end[1]+1))

		print()
		raise SyntaxError('{} Unexpected closing paren'.format(prefix))

	def unexpected_eof_error(self, pos):
		line, col = pos
		prefix = '{}:{}:{}:'.format(self.filename, line, col)
		print('{} error: Unexpected EOF'.format(prefix))
		print('{}  hint: Did you forget to close a paren?'.format(' '*len(prefix)))
		self.print_line_error((line, col), note=' EOF')

		print('{}  note: There are {} unclosed parens'.format(' '*len(prefix), len(self.opening_stack)))
		for (tok, annotation, unclosed_pos) in self.opening_stack:
			print('{}  note: unclosed paren'.format(prefix))
			self.print_line_error(unclosed_pos, pos)

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

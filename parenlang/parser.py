import re

class Parser:
	"""
	In comes string
	Out goes parse tree (which looks something like [[], [[], [],[]]])
	"""
	def __init__(self, instr, filename='<nil>'):
		self.filename = filename
		self.instr = instr # input string
		self.remaining = instr # String that's not yet parsed
		self.lines = [] # List of lines that have been parsed
		self.curlinepos = 0 # The position of the current line
		self.line = 1 # Current line number
		self.col = 1 # Current column number
		self.out = [] # Output paren
		self.parenpos = [] # List of positions of top level parens
		self.parenstack = [] # Stack of open paretheses to be closed

	def parse(self):
		"""
		Parses into a list of lists of lists...
		"""
		while len(self.remaining) > 0:
			self.peek() # Just advance the position so we can get the line/col
			line, col = self.line, self.col
			parsed = self.parse_paren()
			if parsed != None:
				self.out.append(parsed)
				self.parenpos.append((line, col))
		return self.out

	def parse_paren(self):
		"""
		Recursive part of the parser.
		Returns the processed paren (list of lists of lists...).
		"""
		out = []

		tok = self.peek()
		if tok == None:
			return None

		if tok != '(':
			self.unexpected_closing_error()

		self.parenstack.append((self.line, self.col))
		self.eat()

		while len(self.remaining) > 0:
			tok = self.peek()
			if tok == '(':
				parsed = self.parse_paren()
				out.append(parsed)
			elif tok == ')':
				self.eat()
				self.parenstack.pop()
				return out
			else:
				break
		self.unexpected_eof_error()

	def eat(self):
		"""
		Returns the next token.
		Also removes the token from the remaining string so the next token can
		be parsed.
		"""
		tok = self.peek()
		self.remaining = self.remaining[1:]
		self.col += 1
		return tok

	def peek(self):
		"""
		Returns the next token.

		Also advances the current position up to the token (so that
		self.remaining[0] contains the token)
		"""
		for i, c in enumerate(self.remaining):
			if c == '\n':
				self.line += 1
				self.lines.append(self.instr[self.curlinepos:self.curlinepos+self.col-1])
				self.curlinepos += self.col
				self.col = 1
				continue
			if c in ['(', ')']:
				self.remaining = self.remaining[i:]
				return c
			self.col += 1
		self.remaining = ''
		return None

	def get_current_line(self):
		newlinepos = self.instr[self.curlinepos:].find('\n')
		if newlinepos == -1:
			return self.instr[self.curlinepos:]
		else:
			return self.instr[self.curlinepos:self.curlinepos+newlinepos]

	def unexpected_closing_error(self):
		# linenumber = str(len(self.lines)+1)
		# linenumberlength = len(str(len(self.lines)+1))
		prefix = '{}:{}:{}:'.format(self.filename, self.line, self.col)
		print('{} error: Expected ( but got ) instead.'.format(prefix))
		print('{}  hint: Did you forget to remove a closing paren?'.format(' '*len(prefix)))
		self.print_line_error((self.line, self.col))
		# print(self.get_current_line())
		# print(' '*(self.col-1) + '^')
		if len(self.parenpos) > 0:
			print('{}  note: Previous paren starts here'.format(' '*len(prefix)))
			lastline, lastcol = self.parenpos[-1]
			self.print_line_error((lastline, lastcol), (self.line, self.col))
			# if lastline-1 < len(self.lines):
			#	print(self.lines[lastline-1])
			#	if lastline == self.line:
			#		print(' '*(lastcol-1) + '^' + '~'*(self.col-lastcol-1))
			#	else:
			#		print(' '*(lastcol-1) + '^' + '~'*(len(self.lines[lastline-1])-lastcol))
			# else:
			#	print(self.get_current_line())
			#	print(' '*(lastcol-1) + '^' + '~'*(self.col-lastcol-1))
		print()
		raise SyntaxError('{} Unexpected closing paren'.format(prefix))

	def unexpected_eof_error(self):
		prefix = '{}:{}:{}:'.format(self.filename, self.line, self.col)
		print('{} error: Unexpected EOF'.format(prefix))
		print('{}  hint: Did you forget to close a paren?'.format(' '*len(prefix)))
		self.print_line_error((self.line, self.col), note=' EOF')
		# print(self.get_current_line())
		# print(' '*(self.col-1) + '^ EOF')
		print('{}  note: There are {} unclosed parens'.format(' '*len(prefix), len(self.parenstack)))
		for paren in self.parenstack:
			prefix = '{}:{}:{}:'.format(self.filename, paren[0], paren[1])
			print('{}  note: unclosed paren'.format(prefix))
			self.print_line_error(paren, (self.line, self.col))
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

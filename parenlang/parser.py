import re

def parse(instr):
	"""
	Parses the given string into a list of lists of lists...
	"""

	out = []

	remaining = instr
	while len(remaining) > 0:
		parsed, remaining = _parse(remaining)
		if parsed != None:
			out.append(parsed)
	return out

def _parse(instr):
	"""
	Recursively parses. Returns a tuple of a processed paren (list
	of lists of lists...) and the remaining unprocessed string.
	"""

	out = []

	tok, remaining = _gettoken(instr)

	if tok == None:
		# This is a rather special case, which can only happen
		# if given a string without any parens in it.
		return None, ''

	if tok != '(':
		raise ValueError('Expected ( but got ) instead. (Did you forget to remove a closing paren?)')

	remaining = remaining[1:]
	while len(remaining) > 0:
		tok, remaining = _gettoken(remaining)
		if tok == '(':
			parsed, remaining = _parse(remaining)
			out.append(parsed)
		elif tok == ')':
			return out, remaining[1:]
		else:
			break
	raise ValueError('Unexpected EOF (Did you forget to close a paren?)')

def _gettoken(instr):
	"""
	Iterates over the string until it gets a valid token, then
	returns the token and the remaining string (but includes the token).

	In this case, it just iterates until it finds either a (
	or a ).
	"""

	for i, c in enumerate(instr):
		if c in ['(', ')']:
			return c, instr[i:]
	return None, ''

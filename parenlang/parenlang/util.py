import inspect
from functools import wraps

def auto_assign(f):
	"""
	Assigns its arguments to instance attributes.
	"""
	signature = inspect.signature(f)
	@wraps(f)
	def _wrap(*args, **kwargs):
		instance = args[0]
		bind = signature.bind(*args, **kwargs)
		for i, param in enumerate(signature.parameters.values()):
			if i == 0:
				continue
			if param.name in bind.arguments:
				setattr(instance, param.name, bind.arguments[param.name])
			if param.name not in bind.arguments and param.default is not param.empty:
				setattr(instance, param.name, param.default)
		return f(*args, **kwargs)
	return _wrap

def random_paren(k, r=0):
	out = ''
	while k > 0:
		# if k == 0:
		#     return ''
		prob_right = r * (k + r + 2) / 2 / k / (r + 1)
		is_right = random.random() <= prob_right
		if is_right:
			out += ')'
			k -= 1
			r -= 1
			# return ')' + random_paren(k-1, r-1)
		else:
			out += '('
			k -= 1
			r += 1
			# return '(' + random_paren(k-1, r+1)
	return out

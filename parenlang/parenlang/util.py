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

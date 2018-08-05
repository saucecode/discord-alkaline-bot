import re, cmath, math, inspect, readline

'''OPERATIONS = {
	'+' : lambda a,b: Symbol(a.value+b.value),
	'-' : lambda a,b: Symbol(a.value-b.value),
	'/' : lambda a,b: Symbol(b.value/a.value),
	'*' : lambda a,b:Symbol(a.value*b.value),
	'**' : lambda a,b:Symbol(b.value**a.value),
	'sin' : lambda a:Symbol(cmath.sin(a.value)),
	'cos' : lambda a:Symbol(cmath.cos(a.value)),
	'tan' : lambda a:Symbol(cmath.tan(a.value)),
	'atan' : lambda a:Symbol(cmath.atan(a.value)),
	'asin' : lambda a:Symbol(cmath.asin(a.value)),
	'acos' : lambda a:Symbol(cmath.acos(a.value)),
	'sqrt' : lambda a:Symbol(a.value**0.5),
	'%' : lambda a,b:Symbol(b.value%a.value),
	'ln' : lambda a:Symbol(cmath.log(a.value)),
	'log' : lambda a,b:Symbol(cmath.log(b.value,a.value)),
	'rad' : lambda a:Symbol(math.radians(a.value.real)),
	'deg' : lambda a:Symbol(math.degrees(a.value.real)),
	
	'arg' : lambda a:Symbol(cmath.phase(a.value)),
	'abs' : lambda a:Symbol( (a.value.real*a.value.real + a.value.imag*a.value.imag)**0.5),
	'Re' : lambda a:Symbol(a.value.real),
	'Im' : lambda a:Symbol(a.value.imag),
}'''

variables = {}

def variableAssign(value, variable):
	if not variable.type == 'variable' or not value.type in ['number', 'dimension']:
		raise Exception('Assignment expected variable and number|dimension. Got:',variable.type, value.type)
		return
	
	variables[variable.value] = value
	if variable.value[0] == '-':
		variables[variable.value[1:]] = value.__mul__(Symbol('-1'))
	else:
		variables['-'+variable.value] = value.__mul__(Symbol('-1'))
	return variables[variable.value]
	

OPERATIONS = {
	'+' : lambda a,b:a+b,
	'-' : lambda a,b:b-a,
	'/' : lambda a,b:b.__divmod__(a),
	'*' : lambda a,b:a*b,
	'**' : lambda a,b:a.pow(b),
	'sin' : lambda a:a.trigfunc(cmath.sin),
	'cos' : lambda a:a.trigfunc(cmath.cos),
	'tan' : lambda a:a.trigfunc(cmath.tan),
	'atan' : lambda a:a.trigfunc(cmath.atan),
	'asin' : lambda a:a.trigfunc(cmath.asin),
	'acos' : lambda a:a.trigfunc(cmath.acos),
	'sqrt' : lambda a:a.pow(Symbol('0.5')),
	'%' : lambda a,b:b%a,
	'ln' : lambda a:a.log(),
	'log' : lambda a,b:a.log(b),
	'rad' : lambda a:a.trigfunc(lambda z: math.radians(z.real)),
	'deg' : lambda a:a.trigfunc(lambda z: math.degrees(z.real)),
	
	'arg' : lambda a:a.trigfunc(cmath.phase),
	'abs' : lambda a:a.trigfunc( lambda z:(z.real*z.real + z.imag*z.imag)**0.5 ),
	'Re' : lambda a:a.real,
	'Im' : lambda a:a.imag,
	
	'=': variableAssign
}

def countFunctionArguments(func):
	try:
		return len(inspect.signature(func).parameters)
	except:
		return len(inspect.getargspec(func).args)

regexpr = '(\\.|\\/)?(m|s|kg|K|C)(\\^\\d+(\\.\\d*)?)?'

def is_number(s):
	try:
		complex(s)
		return True
	except ValueError:
		return False

def find_units(groups : str):
	units = {}
	
	for matches in groups:
		if not matches[1] in units:
			units[matches[1]] = 0
	
		exponent = 1
	
		if matches[2]:
			exponent = float(matches[2][1:])
	
		if matches[0] in ['', '.']:
			units[matches[1]] += exponent
		else:
			units[matches[1]] -= exponent
	
	return units

class Symbol:
	def __init__(self, val : str, dims = None):
		self.dims = dims
		
		if is_number(val):
			self.type = 'number'
			self.value = complex(val)
		elif val in OPERATIONS:
			self.type = 'operation'
			self.value = val
		elif not val[0].isdigit():
			self.type = 'variable'
			self.value = val
		elif re.findall(regexpr, val) or dims:
			self.type = 'dimension'
			self.value = complex( re.sub(regexpr, '', val) )
			if not dims:
				self.dims = find_units(re.findall(regexpr, val))
		else:
			raise Exception('Symbol unidentified')
		
		if self.dims and any( [self.dims[i]!=0 for i in self.dims] ): self.type = 'dimension'
		
	
	def __add__(self, other):
		print('Adding: {} and {}'.format(self, other))
		if other.type in ['number', 'dimension'] and self.type in ['number', 'dimension']:
			if other.type == 'dimension' and self.dims != other.dims:
				print('WARNING: Mismatched dimensions in addition operation.')
			return Symbol(other.value + self.value, dims=self.dims if self.dims else other.dims)
		raise NotImplementedError('For types: {}, {}'.format(self.type, other.type))
	
	def __sub__(self, other):
		print('Subbing: {} and {}'.format(self, other))
		if other.type in ['number', 'dimension'] and self.type in ['number', 'dimension']:
			if other.type == 'dimension' and self.dims != other.dims:
				print('WARNING: Mismatched dimensions in subtraction operation.')
			return Symbol(other.value - self.value, dims=self.dims if self.dims else other.dims)
		raise NotImplementedError('For types: {}, {}'.format(self.type, other.type))
	
	def __mul__(self, other):
		if other.type in ['number', 'dimension'] and self.type in ['number', 'dimension']:
			new_dims = {}
			for dims in [other.dims or {}, self.dims or {}]:
				for key in dims:
					if not key in new_dims: new_dims[key] = 0
					new_dims[key] += dims[key]
			
			return Symbol(other.value * self.value, dims=new_dims)
		raise NotImplementedError('For types: {}, {}'.format(self.type, other.type))
	
	def __divmod__(self, other):
		if other.type in ['number', 'dimension'] and self.type in ['number', 'dimension']:
			new_dims = {}
			flip = 1
			for dims in [other.dims or {}, self.dims or {}]:
				for key in dims:
					if not key in new_dims: new_dims[key] = 0
					if flip:
						new_dims[key] += dims[key]
					else:
						new_dims[key] += -dims[key]
				flip = 0
			
			return Symbol(other.value / self.value, dims=new_dims)
		raise NotImplementedError('For types: {}, {}'.format(self.type, other.type))
	
	def pow(self, other):
		if other.type in ['number', 'dimension'] and self.type in ['number', 'dimension']:
			if other.type == 'dimension':
				print('WARNING: Exponentiation to a dimensioned number')
			
			new_dims = None
			if self.dims:
				new_dims = {k:self.dims[k]*other.value for k in self.dims or {}}
			
			return Symbol(self.value**other.value, dims=new_dims)
		raise NotImplementedError('For types: {}, {}'.format(self.type, other.type))
	
	def log(self, base=None):
		if base and not base.type in ['number', 'dimension']:
			raise NotImplementedError('For logarithm base type on type'.format(base.type, self.type))
		if not isinstance(base, Symbol):
			if self.type == 'dimension':
				print('WARNING: Natural logarithm of a dimensioned number')
			return Symbol(cmath.log(self.value))
			
		else:
			if self.type == 'dimension':
				print('WARNING: Logarithm of a dimensioned number')
			if base.type == 'dimension':
				print('WARNING: I... what the fuck? Logarithm in a dimensioned base. What are you trying to do? Summon a demon?')
				if base.value.imag != 0:
					print('WARNING: AND an imaginary base!?!! You need help. Here\'s your filthy logarithm.')
			
			return Symbol(cmath.log(self.value, base.value))
		
	
	def trigfunc(self, function):
		if not self.type in ['number', 'dimension']:
			raise NotImplementedError('Trigonometry operation on type {}'.format(self.type))
			return
		
		if self.type == 'dimension':
			print('WARNING: Trigonometry operation on dimensioned number.')
		
		return Symbol(function(self.value))
	
	def __repr__(self):
		return 'Symbol({}, {}, {})'.format(self.type[:3], self.value, self.dims)

def do_postfix(symbols : list):
	symbols = list(symbols)
	while 'operation' in [i.type for i in symbols]:
		sym = [i for i in symbols if i.type == 'operation'][0]
		operation_index = symbols.index(sym)
		arity = countFunctionArguments(OPERATIONS[sym.value])
		segment = symbols[operation_index-arity:operation_index]
		symbols[operation_index-arity:operation_index+1] = [OPERATIONS[sym.value](*segment)]
		
	return symbols

def units_string(units_d : dict):
	if not units_d:
		return ''
	units_d = {**units_d}
	
	for key in units_d:
		units_d[key] = units_d[key].real if isinstance(units_d[key], complex) else units_d[key]
	
	output = ''
	count = 0
	for key in sorted(units_d, key=lambda v:['kg','m','s','K', 'C'].index(v)):
		if units_d[key] == 0: continue
		if units_d[key] > 0:
			if units_d[key] == 1:
				output += '.' + key
			else:
				output += '.{}^{}'.format(key, re.sub('\\.0$', '', str(units_d[key])))
		if units_d[key] < 0:
			if units_d[key] == -1:
				if count == 0:
					output += '{}^-1'.format(key)
				else:
					output += '/{}'.format(key)
			else:
				output += '/{}^{}'.format(key, re.sub('\\d\\.\\0$', '', str(-units_d[key])))
		count += 1
	return output[1:] if output[0] in ['.', '/'] else output

def outputResult(result):
	return ', '.join([ (str(complex(item.value)) if complex(item.value).imag != 0 else str(complex(item.value).real)) + units_string(item.dims) for item in result])

def generate_symbols(instr : str):
	symbols = [Symbol(i) for i in instr.split(' ')]
		
	for index,sym in enumerate(symbols):
		if sym.type == 'variable' and (index+1 >= len(symbols) or not symbols[index+1].value == '=') and sym.value in variables:
			symbols[index] = variables[sym.value]
	
	return symbols

variables = {
	'pi': Symbol(str(cmath.pi)),
	'-pi': Symbol(str(-cmath.pi)),
	'e': Symbol(str(cmath.e)),
	'-e': Symbol(str(-cmath.e)),
	'\\': Symbol('0')
}

def quickly(s : str):
	# string comes in, string goes out. put this on your chatbot. maintains variables state
	symbols_result = do_postfix( generate_symbols(s) )
	result = outputResult( symbols_result )
	variableAssign(symbols_result[0], Symbol('\\'))
	return result

if __name__ == '__main__':
	print('saucecode\'s postfix v8-beta    2018-07-31')
	
	'''
	tests = [
		'10 20 + 5 * 8 /',
		'2s 3 ** -1 sqrt *',
		'1.005kg.m^2/s^2/kg/K 400K * 18kg *',
		'3.14 cos',
		'1.005kg.m^2/s^2/kg/K Cp =', # specific heat of water
		'12kg mass =',
		'400K deltaT =',
		'Cp mass deltaT * * E =',
	]
	
	for test in tests:
		symbols = [Symbol(i) for i in test.split(' ')]
		
		for index,sym in enumerate(symbols):
			if sym.type == 'variable' and (index+1 >= len(symbols) or not symbols[index+1].value == '=') and sym.value in variables:
				symbols[index] = variables[sym.value]
			
		symbols = do_postfix(symbols)
		print(test, '=>', outputResult(symbols))
	'''
	
	while 1:
		userinput = input('>> ')
		if not userinput: continue
		symbols = generate_symbols(userinput)
		
		symbols = do_postfix(symbols)
		print(outputResult(symbols))
		
		# put the top of the stack into the \ variable
		variableAssign(symbols[0], Symbol('\\'))

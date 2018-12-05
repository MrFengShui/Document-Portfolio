import ply.lex as lex, ply.yacc as yacc
import sys, traceback
from ast import *
###############################################################################
logs = sys.stderr

def my(self, t=None, v=None, lineno=1):
	self.type, self.value = t, v # return None
	
lex.LexToken.__str__ = lambda self: "(%s, %s)" % (self.type, self.value)
lex.LexToken.__init__ = my

class MyLexer(object):

	keywords = {
		'print' : 'PRINT',
		'while' : 'WHILE'
		}
	
	tokens = [
		'COLON',
		'ASS_EQ',
		'AUG_ASSIGN_PLUS',
		'INT', 'NAME',
		'LT',
		'NEWLINE', 'INDENT', 'DEDENT'
	] + keywords.values() 
	
	t_COLON = r'\:'
	t_LT = r'\<'
	t_ASS_EQ = r'\='
	t_AUG_ASSIGN_PLUS = r'\+='

	def get_newline(self):
		return lex.LexToken('NEWLINE', 1, self.lexer.lineno)

	def get_dedent(self):
		return lex.LexToken('DEDENT', 1, self.lexer.lineno) # important
   
	def t_indent(self, t):
		r'\n[ ]*' # can only use space in indentations (first and final \n added)
		t.lexer.lineno += 1 # keep track of linenos
		if t.lexer.lexpos < len(t.lexer.lexdata) \
				and t.lexer.lexdata[t.lexer.lexpos] == "\n": # empty but not last line
			return None # ignore pure empty lines
		width = len(t.value) - 1 # exclude \n
		last_pos = t.lexer.lexpos - width
		if width == self.indents[-1]:
			return self.get_newline() # same indentation level
		elif width > self.indents[-1]: # one more level
			t.type = 'INDENT'
			t.value = 1
			self.indents.append(width)
			return t
		# try one or more DEDENTS
		ded = 0
		while len(self.indents) > 1:
			self.indents.pop()
			ded += 1
			if width == self.indents[-1]:
				t.type = 'DEDENT'
				t.value = ded # remember how many dedents
				return t
		raise Exception("indent error at line %d:\" %s\"" % (t.lexer.lineno, 
															 self.lines[t.lexer.lineno]))

	def t_space(self, t):
		r'[ ]+'
		return None # ignore white space

	def t_INT(self, t): # t is the current token
		r'(-?)\d+'
		try:
			t.value = int(t.value)
		except ValueError:
			t.value = 0
			raise Exception("integer value too large", t.value)
		return t

	def t_NAME(self, t):
		r'[a-zA-Z_][a-zA-Z_0-9]*'
		t.type = MyLexer.keywords.get(t.value, 'NAME')  # Check for key words first
		return t

	def t_error(self, t):
		raise Exception("Illegal char '%s' (line %d):\" %s\"" % (t.value[0], 
																 t.lexer.lineno, 
																 self.lines[t.lexer.lineno]))
		t.lexer.skip(1)

	def __init__(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs) # build regexps
		self.dedent_balance = 0
		self.indents = [0]

	def input(self, stream):
		stream = "\n" + stream + "\n" 
		self.lexer.lineno -= 1 # remove first line
		self.lexer.input(stream)
		self.lines = stream.split("\n") # internal
		_tokens = [] # can't re-use tokens (needed by lex)
		while True:
			tok = self.lexer.token() # lexer.token
			if not tok:
				break
			if tok.type == 'DEDENT': # multiple dedents
				for _ in range(tok.value):
					_tokens.append(self.get_newline()) # new instance every time
					_tokens.append(self.get_dedent())  # new instance every time
				_tokens.append(self.get_newline()) # N.B.: newline after block
			elif tok.type == 'INDENT':
				_tokens.append(self.get_newline()) # new instance every time
				_tokens.append(tok)
			else:
				_tokens.append(tok)
		self._tokens = _tokens
		self.tokid = 0

	def token(self):
		try:
			self.tokid += 1
			# print self._tokens[self.tokid], 
			return self._tokens[self.tokid]
		except:
			return None

###############################################################################
'''
module      : stmt+
stmt+       : stmt (epsilon | stmt+)
stmt        : (small_stmt+ | while_stmt) NEWLINE
small_stmt+ : small_stmt (epsilon | small_stmt+) NEWLINE
small_stmt  : assign_stmt | print_stmt
assign_stmt : name assigns
assigns     : ("=" | "+=") decint
print_stmt  : "print" name
while_stmt  : "while" name "<" decint ":" suite
suite       : NEWLINE INDENT small_stmt+ DEDENT
'''
precedence = (
		('nonassoc','PRINT'),
		('nonassoc', 'COLON'),
		('nonassoc', 'WHILE'),
		('right', 'LT'),
		('nonassoc', 'INT')
	)

def p_module(t):
	'''
	module : stmts
	'''
	t[0] = Module(body=t[1]) # t[1] is already a list

def p_stmts(t): # flattens into a list
	'''
	stmts : stmt stmt_ext
	'''
	t[0] = [t[1]] + t[2]

def p_stmt_ext(t):
	'''
	stmt_ext : 
			| stmts
	'''
	if len(t) == 1:
		t[0] = []
	else:
		t[0] = t[1]

def p_stmt(t): # flattens into a list
	'''
	stmt : small_stmts NEWLINE
		| while_stmt NEWLINE
	'''
	if isinstance(t[1], While):
		t[0] = t[1]
	else:
		t[0] = t[1][0]

def p_small_stmts(t):
	'''
	small_stmts : small_stmt small_ext
	'''
	t[0] = [t[1]] + t[2]

def p_small_ext(t):
	'''
	small_ext : 
			| small_stmts
	'''
	if len(t) == 1:
		t[0] = []
	else:
		t[0] = t[1]

def p_small_stmt(t):
	'''
	small_stmt : assign_stmt
			| print_stmt
	'''
	t[0] = t[1]

def p_assign_stmt(t):
	'''
	assign_stmt : NAME assign_ext
	'''
	if isinstance(t[2], Assign):
		t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = t[2].value)
	else:
		t[0] = AugAssign(target = Name(id = t[1], ctx = Store()), op = t[2].op, value = t[2].value)

def p_assign_ext(t):
	'''
	assign_ext : ASS_EQ INT
			| AUG_ASSIGN_PLUS INT
	'''
	if t[1] == '=':
		t[0] = Assign(targets = [Name(id = None, ctx = Store())], value = Num(n = t[2]))
	else:
		t[0] = AugAssign(target = Name(id = None, ctx = Store()), op = Add() if t[1] == '+=' else Sub(), value = Num(n = t[2]))

def p_print_stmt(t):
	'''
	print_stmt : PRINT NAME
	'''
	t[0] = Print(dest = None, values=[Name(id = t[2], ctx = Load())], nl = True)

def p_while_stmt(t):
	'''while_stmt : WHILE cmp_expr COLON NEWLINE INDENT stmts DEDENT'''
	t[0] = While(test = t[2], body = t[6], orelse = [])

def p_cmp_expr(t):
	'''cmp_expr : NAME LT INT'''
	t[0] = Compare(left = t[1] if isinstance(t[1], Num) else Name(id = t[1], ctx = Load()), ops = [Lt()], comparators = [Num(n = t[3])])

def p_error(t):
	raise Exception("Syntax error (on line %d): '%s'" % (t.lineno, t.value))

def myresult(r):
	repr_str = mydump(r) # N.B. lhuang hack: dump(r) instead of repr(r)
	if '\n' in repr_str:
		repr_str = repr(repr_str)
	if len(repr_str) > 85:
		# truncate long lines; N.B. lhuang hack: xxxxx ... xxx
		repr_str = "%s...%s" % (repr_str[:70], repr_str[-15:])
	result = repr_str #(type(r).__name__, id(r), repr_str)
	return result

# Format stack entries when the parser is running in debug mode
def mystack(r):
	repr_str = mydump(r)
	if '\n' in repr_str:
		repr_str = repr(repr_str)
	if len(repr_str) < 30:
		return repr_str
	else:
		return "%s...%s" % (repr_str[:15], repr_str[-15:])

yacc.format_result = myresult
yacc.format_stack_entry = mystack

tokens = MyLexer.tokens # important
yacc.yacc()

###############################################################################

# translate

def generate_c(node):
	
	variables = set()

	def _gen(node):
		if isinstance(node, AST):
			if isinstance(node, Module):
				return "\n".join(["#include <stdio.h>",
								  "int main()",
								  "{", 
								  "\n".join(_gen(stmt) for stmt in node.body), 
								  "return 0;",
								  "}"])
			elif isinstance(node, Print): 
				format = "\"%s\\n\"" % " ".join("%d" for x in node.values)
				items = ", ".join(_gen(x) for x in node.values)
				return 'printf(%s, %s);' % (format, items)
			elif isinstance(node, Num):
				return '(%s)' % node.n
			elif isinstance(node, Assign):
				line = "%s = %s;" % (_gen(node.targets[0]),
									 _gen(node.value))
				return line
			elif isinstance(node, AugAssign):
				if isinstance(node.op, Add):
					return "%s += %s;\n" % (_gen(node.target), _gen(node.value))
			elif isinstance(node, Name):
				if isinstance(node.ctx, Load): # R-value
					return node.id
				elif node.id in variables:                    
					return node.id
				else: 
					variables.add(node.id)
					return "int %s" % node.id
			elif isinstance(node, While):
				body = ""
				for item in node.body:
					body += _gen(item)
				return "while(%s)\n{\n" % _gen(node.test) + body + "\n}\n"
			elif isinstance(node, Compare):
				if isinstance(node.ops[0], Lt):
					return "%s %s %s" % (_gen(node.left), "<", _gen(node.comparators[0]))
			else:
				raise Exception('Error in _gen: unrecognized AST node: %s' % ast.dump(node))
		else:
			raise Exception('Error in _gen: unrecognized non-AST of %s: %s' % (str(type(node))[1:-1], str(node)))

	return _gen(node)


###############################################################################
# Main

if __name__ == "__main__":
	try:
		txt = sys.stdin.read()
		mylexer = MyLexer()
		tree = yacc.parse(txt, lexer = mylexer, debug = 0)
		# print '\n\n', dump(tree), '\n\n', dump(parse(txt))
		print generate_c(tree)
	except Exception as e:
		print >> logs, e
		traceback.print_exc(file = logs)

#!/usr/bin/env python2.7
import sys, traceback, ply.lex as lex, ply.yacc as yacc
from ast import *

op_list, cmpr_list = [], []
cmp_op_dict = {'<': Lt(), '>': Gt(), '==': Eq(), '<=': LtE(), '>=': GtE(), '<>': NotEq(), '!=': NotEq()}
logs = sys.stderr
###############################################################################
# Lexer
def my(self, t=None, v=None, lineno=1):
	self.type, self.value = t, v # return None
	
lex.LexToken.__str__ = lambda self: "(%s, %s)" % (self.type, self.value)
lex.LexToken.__init__ = my

class MyLexer(object):

	keywords = {
		'print': 'PRINT',
		'if': 'IF',
		'else': 'ELSE',
		'for': 'FOR',
		'in': 'IN',
		'range': 'RANGE',
		'not': 'NOT',
		'and': 'AND',
		'or': 'OR'
	}

	tokens = [
		'FOR',
		'PRINT', 
		'INDENT', 'DEDENT', 'NEWLINE',
		'COLON', 'COMMA', 'SEMICOLON',
		'ELSE', 'IF', 
		'AND', 'OR',
		'IN', 
		'RANGE',
		'NAME',
		'ASSIGN',
		'INT', 
		'TRUE', 'FALSE',
		'LT', 'GT', 'EQ', 'LTE', 'GTE', 'NOTEQA', 'NOTEQB',
		'NOT',
		'PLUS',
		'USUB',
		'LPRN', 'RPRN'
	]
	
	#t_ignore = ' \t'
	t_FOR = r'for'
	t_PRINT = r'print'
	t_COLON = r'\:'
	t_COMMA = r'\,'
	t_SEMICOLON = r'\;'
	t_ELSE = r'else'
	t_IF = r'if'
	t_AND = r'and'
	t_OR = r'or'
	t_PLUS = r'\+'
	t_USUB = r'\-'
	t_IN = r'in'
	t_RANGE = r'range'
	t_ASSIGN = r'\='
	t_NOT = r'not'
	t_TRUE = r'True'
	t_FALSE = r'False'
	t_LT = r'\<'
	t_GT = r'\>'
	t_EQ = r'\=='
	t_LTE = r'\<='
	t_GTE = r'\>='
	t_NOTEQA = r'\<>'
	t_NOTEQB = r'\!='
	t_LPRN = r'\('
	t_RPRN = r'\)'

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

		if width > self.indents[-1]: # one more level
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

		raise Exception("indent error at line %d:\" %s\"" % (t.lexer.lineno, self.lines[t.lexer.lineno]))

	def t_space(self, t):
		r'[ ]+'
		return None # ignore white space

	#t_ignore = ' \t'                 # ignore spaces

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
		raise Exception("Illegal character '%s' in line %d:\" %s\"" % (t.value[0], 
																	   t.lexer.lineno, 
																	   self.lines[t.lexer.lineno]))
		t.lexer.skip(1)

	def __init__(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs) # build regexps
		self.dedent_balance = 0
		self.indents = [0]

	def input(self, stream):
		# the initial \n is to simplify indent
		# the final \n is to simplify dedent
		stream = "\n" + stream + "\n" 
		self.lexer.lineno -= 1 # remove first line
		self.lexer.input(stream)
		self.lines = stream.split("\n") # internal		
		#print >> logs, "now lexing..."

		_tokens = [] # can't re-use tokens (needed by lex)
		while True:
			tok = self.lexer.token() # lexer.token

			if not tok: break
			if tok.type == 'DEDENT': # multiple dedents
				for _ in range(tok.value):
					_tokens.append(self.get_newline()) # new instance every time
					_tokens.append(self.get_dedent())  # new instance every time
				_tokens.append(self.get_newline()) # N.B.: newline after block
			elif tok.type == 'INDENT':
				_tokens.append(self.get_newline()) # new instance every time
				_tokens.append(tok)
			else:
				# normal token
				_tokens.append(tok)
		
		self._tokens = _tokens
		self.tokid = 0 # prepare for token()

	def token(self):
		try:
			self.tokid += 1
			return self._tokens[self.tokid]
		except:
			return None

###############################################################################
# Parser
precedence = (
		('nonassoc', 'FOR'),
		('nonassoc', 'PRINT'),
		('nonassoc', 'COMMA', 'COLON', 'SEMICOLON'),
		('right', 'ELSE', 'IF'),
		('left', 'OR'),
		('left', 'AND'),
		('nonassoc', 'IN'),
		('nonassoc', 'RANGE'),
		('nonassoc', 'NAME'),		
		('left', 'ASSIGN'),
		('nonassoc', 'TRUE', 'FALSE'),
		('right', 'LT', 'GT', 'EQ', 'LTE', 'GTE', 'NOTEQA', 'NOTEQB'),
		('left', 'PLUS'),
		('nonassoc', 'USUB', 'NOT'),
		('nonassoc', 'LPRN', 'RPRN')
	)

def p_module(t):
	'''module : stmtlist'''
	t[0] = Module(body=t[1]) # t[1] is already a list

def p_stmtlist(t): # flattens into a list
	'''stmtlist : stmt 
				| stmt stmtlist '''
	if len(t) == 2:
		t[0] = [t[1]]
	else:
		t[0] = [t[1]] + t[2]

# stmt : (simple_stmt | if_stmt | for_stmt) NEWLINE
def p_mono_stmt(t):
	'''stmt : simple_stmt NEWLINE
			| if_stmt NEWLINE
			| for_stmt NEWLINE'''
	t[0] = t[1]

# simple_stmt : "print" expr ("," expr)*
# 			| name "=" expr
def p_print_stmt(t):
	'''simple_stmt : PRINT expr
					| PRINT expr print_expr'''
	if len(t) == 3:
		if not isinstance(t[2], Num) and not isinstance(t[2], BinOp):
			t[0] = Print(dest = None, values = [Name(id = t[2], ctx = Load())], nl = True)
		else:
			t[0] = Print(dest = None, values = [t[2]], nl = True)
	else:
		if not isinstance(t[2], Num) and not isinstance(t[2], BinOp):
			t[0] = Print(dest = None, values = [Name(id = t[2], ctx = Load())] + t[3], nl = True)
		else:
			t[0] = Print(dest = None, values = [t[2]] + t[3], nl = True)
def p_mprint_stmt(t):
	'''print_expr : COMMA expr
				| COMMA expr print_expr'''
	if len(t) == 3:
		if not isinstance(t[2], Num) and not isinstance(t[2], BinOp):
			t[0] = [Name(id = t[2], ctx = Load())]
		else:
			t[0] = [t[2]]
	else:
		if not isinstance(t[2], Num) and not isinstance(t[2], BinOp):
			t[0] = [Name(id = t[2], ctx = Load())] + t[3]
		else:
			t[0] = [t[2]] + t[3]

def split(ops, cmprs, src):
	if isinstance(src.comparators[0], Compare):
		ops.append(src.ops[0])
		cmprs.append(src.comparators[0].left if isinstance(src.comparators[0].left, Num) or isinstance(src.comparators[0].left, BinOp) or isinstance(src.comparators[0].left, UnaryOp) or isinstance(src.comparators[0].left, IfExp) else Name(id = src.comparators[0].left, ctx = Load()))
		return split(ops, cmprs, src.comparators[0])
	else:
		ops.append(src.ops[0])
		cmprs.append(src.comparators[0] if isinstance(src.comparators[0], Num) or isinstance(src.comparators[0], BinOp)  or isinstance(src.comparators[0], UnaryOp)  or isinstance(src.comparators[0], IfExp) else Name(id = src.comparators[0], ctx = Load()))
		return ops, cmprs

def p_assign_stmt(t):
	'simple_stmt : name ASSIGN expr'
	if isinstance(t[3], Compare):
		op, cmpr = split([], [], t[3])
		t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = Compare(left = t[3].left if isinstance(t[3].left, Num) or isinstance(t[3].left, BinOp)  or isinstance(t[3].left, UnaryOp) or isinstance(t[3].left, IfExp) else Name(id = t[3].left, ctx = Load()), ops = op, comparators = cmpr))
	elif isinstance(t[3], IfExp):
		if isinstance(t[3].test, IfExp):
			op, cmpr = split([], [], t[3].test.test)
			t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = IfExp(test = IfExp(test = Compare(left = t[3].test.test.left if isinstance(t[3].test.test.left, Num) or isinstance(t[3].test.test.left, BinOp)  or isinstance(t[3].test.test.left, UnaryOp) else Name(id = t[3].test.test.left, ctx = Load()), ops = op, comparators = cmpr), body = t[3].test.body, orelse = t[3].test.orelse), body = t[3].body, orelse = t[3].orelse))

		if isinstance(t[3].test, Compare):
			op, cmpr = split([], [], t[3].test)
			
			t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = IfExp(test = Compare(left = t[3].test.left if isinstance(t[3].test.left, Num) or isinstance(t[3].test.left, BinOp)  or isinstance(t[3].test.left, UnaryOp) else Name(id = t[3].test.left, ctx = Load()), ops = op, comparators = cmpr), body = t[3].body, orelse = t[3].orelse))
	elif t[3] == 'True' or t[3] == 'False':
		t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = Name(id = t[3], ctx = Load()))
	else:
		t[0] = Assign(targets = [Name(id = t[1], ctx = Store())], value = t[3] if isinstance(t[3], Num) or isinstance(t[3], BinOp) or isinstance(t[3], UnaryOp) or isinstance(t[3], BoolOp) else Name(id = t[3], ctx = Load()))

# if_stmt : "if" expr ":" (simple_stmts | suite)
def p_if_stmt(t):
	'''if_stmt : IF expr COLON simple_stmts
				| IF expr COLON suite'''
	if isinstance(t[2], Compare):
		if not isinstance(t[2].comparators[0], Num):
			op, cmpr = split(t[2].ops, [], t[2].comparators[0])
			t[0] = If(test = Compare(left = t[2].left if isinstance(t[2].left, Num) or isinstance(t[2].left, UnaryOp) or isinstance(t[2].left, BinOp) or isinstance(t[2].left, IfExp) else Name(id = t[2].left, ctx = Load()), ops = op, comparators = [t[2].comparators[0].left if isinstance(t[2].comparators[0].left, Num) or isinstance(t[2].comparators[0].left, UnaryOp) or isinstance(t[2].comparators[0].left, BinOp) or isinstance(t[2].comparators[0].left, IfExp) else Name(id = t[2].comparators[0].left, ctx = Load())] + cmpr), body = t[4], orelse = [])
		else:
			t[0] = If(test = t[2], body = t[4], orelse = [])
	else:
		t[0] = If(test = t[2], body = t[4], orelse = [])

# for_stmt : "for" name "in" "range" "(" expr ")" ":" (simple_stmts | suite)
def p_for_stmt(t):
	'''for_stmt : FOR name IN RANGE LPRN expr RPRN COLON simple_stmts
				| FOR name IN RANGE LPRN expr RPRN COLON suite'''
	t[0] = For(target = Name(id = t[2], ctx = Store()), iter = Call(func = Name(id = 'range', ctx = Load()), args = [t[6] if isinstance(t[6], Num) or isinstance(t[6], BinOp) or isinstance(t[6], IfExp) or isinstance(t[6], BoolOp) else Name(id = t[6], ctx = Load())], keywords = [], starargs = None, kwargs = None), body = t[9], orelse = [])

# simple_stmts : simple_stmt (";" simple_stmt)+
def p_simple_stmts(t):
	'''simple_stmts : simple_stmt
					| simple_stmt SEMICOLON simple_stmts'''
	if len(t) == 2:
		t[0] = [t[1]]
	else:
		t[0] = [t[1]] + t[3]

# suite : NEWLINE INDENT stmt+ DEDENT
def p_suite(t):
	'suite : NEWLINE INDENT stmtlist DEDENT'
	t[0] = t[3]

# expr : name
# 		| decint
# 		| "-" expr
#		| expr "+" expr
# 		| "(" expr ")"
#		| expr "if" expr "else" expr
#		| expr "and" expr
#		| expr "or" expr
#		| "not" expr
#		| expr (comp_op expr)+
#		| "True"
#		| "False"
#		| expr "if" expr "else" expr
def p_expr_name(t):
	'name : NAME'
	t[0] = t[1]
def p_vary_expr(t):
	'expr : name'
	t[0] = t[1]
def p_int_expr(t):
	'expr : INT'
	t[0] = Num(n = t[1])
def p_unary_expr(t):
	'''expr : USUB expr
			| NOT expr'''
	if not isinstance(t[2], Num):
		t[0] = UnaryOp(op = USub(), operand = Name(id = t[2], ctx = Load()))
	else:
		t[0] = UnaryOp(op = USub(), operand = t[2])
def p_plus_expr(t):
	'expr : expr PLUS expr'
	lhs, rhs = t[1], t[3]
	
	if not isinstance(lhs, Num) and not isinstance(lhs, UnaryOp) and not isinstance(lhs, BinOp): lhs = Name(id = t[1], ctx = Load())
	if not isinstance(rhs, Num) and not isinstance(rhs, UnaryOp) and not isinstance(rhs, BinOp) and not isinstance(rhs, BoolOp): rhs = Name(id = t[3], ctx = Load())
	t[0] = BinOp(left = lhs, right = rhs, op = Add())
def p_paren_expr(t):
	'expr : LPRN expr RPRN'
	t[0] = t[2]
def p_bool_calc_expr(t):
	'''expr : expr AND expr
			| expr OR expr'''
	if t[2] == 'and':
		t[0] = BoolOp(op = And(), values = [t[1], t[3]])
	else:
		t[0] = BoolOp(op = Or(), values = [t[1], t[3]])
def p_bool_value_expr(t):
	'''expr : TRUE
			| FALSE'''
	t[0] = str(t[1])
def p_if_expr(t):
	'expr : expr IF expr ELSE expr'
	lhs = t[1]
	rhs = t[5]
	if t[1] == 'True' or t[1] == 'False': lhs = Name(id = t[1], ctx = Load())
	if t[5] == 'True' or t[5] == 'False': rhs = Name(id = t[5], ctx = Load())

	if isinstance(t[3], IfExp):
		op, cmpr = split([], [], t[3].test)
		t[0] = IfExp(test = t[3], body = Name(id = lhs, ctx = Load()) if not isinstance(lhs, BinOp) and not isinstance(lhs, Num) else lhs, orelse = Name(id = rhs, ctx = Load()) if not isinstance(rhs, BinOp) and not isinstance(rhs, Num) and not isinstance(rhs, IfExp) else rhs)
	elif isinstance(t[3], BoolOp):
		for value in t[3].values:
			if isinstance(value, Compare):
				value.left = value.left if isinstance(value.left, Num) or isinstance(value.left, BinOp) or isinstance(value.left, IfExp) or isinstance(value.left, UnaryOp) else Name(id = value.left, ctx = Load())
		t[0] = t[3]
	else:
		t[0] = IfExp(test = t[3], body = lhs, orelse = rhs)

# comp_op : '<' | '>' | '==' | '>=' | '<=' | '<>' | '!='
def p_cmp_expr(t):
	'''expr : expr LT expr
			| expr GT expr
			| expr EQ expr
			| expr LTE expr
			| expr GTE expr
			| expr NOTEQA expr
			| expr NOTEQB expr'''
	t[0] = Compare(left = t[1], ops = [cmp_op_dict[t[2]]], comparators = [t[3]])

def p_error(t):
	raise Exception("Syntax error (on line %d): '%s'" % (t.lineno, t.value))

tokens = MyLexer.tokens # important
yacc.yacc()

###############################################################################
# Main
def generate_c(node):
    variables = {} # var_name -> value
    var_types = {} # var_name -> type
    
    def make_loop_var(s):
        while s in variables:
            s += "_"
        return s
    
    def output_form(s, node): # s is _gen(node)
        if node._type == int: 
            return s
        elif node._type == bool:
            return '((%s)? "True" : "False")' % s
        else:
            raise Exception("can only print int or bool expr!")

    def _gen(node, in_block=False, top_block=True):
        if isinstance(node, AST):
            if isinstance(node, Module):
                return "\n".join(["#include <stdio.h>",
                                  "int main()",
                                  "{", 
                                  _gen(node.body), 
                                  "return 0;",
                                  "}"])
            elif isinstance(node, Print): 
                # N.B.: must call _gen() first to figure out type
                items = ", ".join(output_form(_gen(x), x) for x in node.values)
                format = "\"%s\\n\"" % " ".join({int: "%d", bool:"%s"}[x._type] for x in node.values)
                return 'printf(%s, %s);' % (format, items)
            elif isinstance(node, Num):
                node._type = int
                return '(%s)' % node.n
            elif isinstance(node, UnaryOp) and isinstance(node.op, USub):
                s = _gen(node.operand)
                assert node.operand._type == int, "type mismatch"
                node._type = int
                return "(-%s)" % s
            elif isinstance(node, BinOp):
                lefts, rights = _gen(node.left), _gen(node.right)
                assert node.left._type == node.right._type == int, "type mismatch"
                node._type = int
                if isinstance(node.op, Add):
                    op = "+"
                elif isinstance(node.op, Sub):
                    op = "-"
                elif isinstance(node.op, Mult):
                    op = "*"
                else:
                    op = "/"
                return '(%s%s%s)' % (lefts, op, rights)
            elif isinstance(node, Assign): # handle all assignment here
                var_name = _gen(node.targets[0].id) # py_var
                value_s = _gen(node.value)
                
                if var_name in variables: # reassignment
                    #assert var_types[var_name] == node.value._type, "reassignment to different type"
                    #actually it's fine to reassign to a different type! (int/bool)
                    prefix = ""                    
                else: # new variable assignment
                    variables[var_name] = None # blank place-holder
                    var_types[var_name] = node.value._type
                    # do not declare anything in loop!
                    if in_block:
                        prefix = ""
                    else:
                        prefix = "int " # works for bool as well
                line = "%s%s = %s;" % (prefix, var_name, value_s)
                variables[var_name] = node.value # assigned
                var_types[var_name] = node.value._type
                node._type = node.value._type
                return line

            elif isinstance(node, Name):
                assert isinstance(node.ctx, Load)
                if node.id in ["True", "False"]:
                    node._type = bool
                    return str((int)(eval(node.id)))
                var_name = _gen(node.id)
                if var_name not in variables or variables[var_name] is None:
                    raise Exception("undefined variable %s in Python code" % var_name)
                node._type = var_types[var_name] # last assigned type
                return var_name

            elif isinstance(node, If):
                test = _gen(node.test)
                current_vars = set(variables.keys()) # make a snapshot of current vars
                body = _gen(node.body, in_block=True, top_block=False) 
                # declare local vars used in the if body outside of the top-level block
                if top_block:
                    declars = "\n".join("int %s;" % x for x in variables.keys() if x not in current_vars) 
                else:
                    declars = ""
                return "\n".join([declars,
                                  "if (%s)" % test,
                                  "{",
                                  body,
                                  "}"])

            elif isinstance(node, Compare):
                operand_nodes = [node.left] + node.comparators
                operands = map(_gen, operand_nodes)
                assert all(x._type == int for x in operand_nodes), "can only compare int_exprs"
                node._type = bool
                ops = map(_gen, node.ops)
                return "(%s)" % " && ".join("(%s %s %s)" % (x, op, operands[i+1])
                                            for i, (op, x) in enumerate(zip(ops, operands)))

            elif isinstance(node, Lt):
                return "<"
            elif isinstance(node, Eq):
                return "=="
            elif isinstance(node, Gt):
                return ">"
            elif isinstance(node, GtE):
                return ">="
            elif isinstance(node, LtE):
                return "<="
            elif isinstance(node, NotEq):
                return "!=" # <> or !=

            elif isinstance(node, IfExp):
                test_s = _gen(node.test)
                body_s = _gen(node.body)
                else_s = _gen(node.orelse)
                assert node.body._type == node.orelse._type, "type mismatch in IfExp"
                node._type = node.body._type
                return "((%s) ? (%s) : (%s))" % (test_s, body_s, else_s)

            elif isinstance(node, BoolOp):                
                node._type = bool
                operand_nodes = node.values
                operands = map(_gen, operand_nodes)
                op_s = _gen(node.op)
                assert all(x._type == bool for x in operand_nodes)
                return "(%s)" % op_s.join(operands)

            elif isinstance(node, UnaryOp) and isinstance(node.op, Not):
                node._type = bool
                s = _gen(node.operand)
                assert node.operand._type == bool
                return "! (%s)" % s

            elif isinstance(node, Or):
                return " || "
            elif isinstance(node, And):
                return " && "

            elif isinstance(node, For) and isinstance(node.iter, Call) \
                    and node.iter.func.id == "range":
                
                current_vars = set(variables.keys()) # make a snapshot of current vars
                var_out = _gen(node.target.id)   # i       
                variables[var_out] = 0
                var_types[var_out] = int
                limit_s = _gen(node.iter.args[0]) # cache the ... in range(...)
                body_s = _gen(node.body, in_block=True, top_block=False) 
                # declare local vars used in the loop body outside of the top-level block

                if top_block:
                    declars = "\n".join("int %s;" % x for x in variables.keys() if x not in current_vars) 
                else:
                    declars = ""

                # important: loop var and limit var can be reused
                # so we don't add them to variables!
                var_in = make_loop_var(node.target.id + "_")                
                limit_var = make_loop_var(var_in + "limit")

                return "\n".join([declars,
                                  "for (int %s = 0, %s = %s; %s < %s; %s++)" % (var_in,
                                                                                limit_var,
                                                                                limit_s,
                                                                                var_in,
                                                                                limit_var,
                                                                                var_in),
                                  "  { %s = %s; %s }" % (var_out, var_in, body_s)])
            else:
                raise Exception('Error in _gen: unrecognized AST node: %s' % ast.dump(node))
        elif isinstance(node, list): # list of nodes
            return "\n".join(_gen(stmt, in_block, top_block) for stmt in node)
        elif isinstance(node, str): # Name.id str
            return "py_%s" % node # avoid keywords in C
        else:
            raise Exception('Error in _gen: unrecognized non-AST of %s: %s' % (str(type(node))[1:-1], str(node)))

    return _gen(node)

if __name__ == "__main__":
	try:
		mylexer = MyLexer()
		tree = yacc.parse(sys.stdin.read(), lexer = mylexer, debug = 0)
		#print dump(tree)
		print generate_c(tree)
	except Exception as e:
		print >> logs, e
		traceback.print_exc(file = logs)

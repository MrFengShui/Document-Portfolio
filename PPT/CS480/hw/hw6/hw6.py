#!/usr/bin/env python2.7

__author__ = 'LUAN SONGJIAN'

import ply.lex as lex
import sys, traceback, types, ast
from ast import *

logs = sys.stderr

###############################################################################
# Lexer
def my(self, t=None, v=None, lineno=1):
	self.type, self.value = t, v # return None
	
lex.LexToken.__str__ = lambda self: '(%s, %s)' % (self.type, self.value)
lex.LexToken.__init__ = my

class MyLexer(object):

	keywords = {
		'print' : 'PRINT', 'while':'WHILE'
	}
	
	tokens = [
		'INDENT', 'DEDENT',  
		'INT',  'NAME',
		'ASSIGN', 'ADD', 'MINUS', 'AUGADD', 
		'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQA', 'NEQB',
		'COLON', 'COMMA',
		'NEWLINE', 'LPAREN', 'RPAREN', 'EOF'
	] + keywords.values() 
	
	t_MINUS = r'-'
	t_ASSIGN = r'='
	t_ADD = r'\+'
	t_AUGADD = r'\+='
	t_LT = r'<'
	t_GT = r'>'
	t_LTE = r'<='
	t_GTE = r'>='
	t_EQ = r'=='
	t_NEQA = r'!='
	t_NEQB = r'<>'
	t_COLON = r'\:'
	t_COMMA = r'\,'
	t_LPAREN = r'\('
	t_RPAREN = r'\)'


	def get_newline(self):
		return lex.LexToken('NEWLINE', 1, self.lexer.lineno)

	def get_dedent(self):
		return lex.LexToken('DEDENT', 1, self.lexer.lineno) # important
   
	def t_indent(self, t):
		r'\n[ ]*' # can only use space in indentations (first and final \n added)
		t.lexer.lineno += 1 # keep track of linenos
		if t.lexer.lexpos < len(t.lexer.lexdata) \
				and t.lexer.lexdata[t.lexer.lexpos] == '\n': # empty but not last line
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
		raise Exception('indent error at line %d: %s' % (t.lexer.lineno, 
															 self.lines[t.lexer.lineno]))

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
			raise Exception('integer value too large', t.value)
		return t

	def t_NAME(self, t):
		r'[a-zA-Z_][a-zA-Z_0-9]*'
		t.type = MyLexer.keywords.get(t.value, 'NAME')  # Check for key words first
		return t

	def t_error(self, t):
		raise Exception('Illegal character [%s] in line %d:\' %s\'' % (t.value[0], 
																	   t.lexer.lineno, 
																	   self.lines[t.lexer.lineno]))
		t.lexer.skip(1)

	def __init__(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs) # build regexps
		self.dedent_balance = 0
		self.indents = [0]

	def input(self, stream):
		stream = '\n' + stream + '\n' 
		self.lexer.lineno -= 1 # remove first line
		self.lexer.input(stream)
		self.lines = stream.split('\n') # internal
		print >> logs, 'now lexing...'
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
				# normal token
				_tokens.append(tok)
		for tok in _tokens:
			print >> logs, tok, # debug
		print >> logs
		_tokens.append(lex.LexToken('EOF', 1, self.lexer.lineno)) # append '$'
		self._tokens = _tokens
		self.tokid = 1 # prepare for token() and peektok()

	def token(self): # eat the next token
		try:
			tok = self._tokens[self.tokid]
			self.tokid += 1
			print >> logs, tok 
			return tok
		except:
			return None

	def peektok(self): # peek but not eat
		return self._tokens[self.tokid]

###############################################################################
# Parser
def parse_module():
	body = parse_stmts()
	return Module(body = body)

def parse_stmts(stmts = []):
	tok = mylexer.peektok()
	# print '$$$', tok
	if tok.type in ('NAME', 'PRINT', 'WHILE'):
		stmt = parse_stmt()
		stmts.append(stmt)
		return parse_stmts(stmts)
	elif tok.type in ('NEWLINE'):
		mylexer.token()
		return parse_stmts(stmts)
	elif tok.type == 'EOF':
		return stmts
	else:
		raise Exception('Unexpected Type in Stmts')

def parse_stmt():
	tok = mylexer.peektok()
	# print '###', tok
	if tok.type in ('NAME', 'PRINT'):
		return parse_simple_stmt()
	elif tok.type in ('WHILE', ''):
		return parse_while_stmt([])
	else:
		raise Exception('Unexpected Type in Stmt')

def parse_simple_stmt():
	tok = mylexer.peektok()
	
	if tok.type == 'NAME':
		return parse_assign_stmt()
	elif tok.type == 'PRINT':
		return parse_print_stmt([])
	else:
		raise Exception('Unexpected Type in Simple Stmt')

def parse_assign_stmt():
	lhs = parse_expr()
	tok = mylexer.token()
	rhs = parse_expr()

	if tok.type == 'ASSIGN':
		return Assign(targets = [lhs], value = rhs)
	else:
		return AugAssign(target = lhs, op = Add(), value = rhs)

def parse_print_stmt(values = []):
	tok = mylexer.peektok()
	
	while tok.type <> 'NEWLINE':
		tok = mylexer.token()
		values.append(parse_expr())
		tok = mylexer.peektok()

	return Print(dest = None, values = values, nl = True)

def parse_while_stmt(suite = []):
	tok = mylexer.token()
	test = parse_expr(None, [], [])
	tok = mylexer.token()
	suite = parse_suite([])
	tok = mylexer.peektok()
	
	if tok.type == 'DEDENT':
		tok = mylexer.token()
		return While(test = test, body = suite, orelse = [])
	else:
		raise Exception('Unexpected Type in While Stmt')

def parse_suite(suite = []):
	tok = mylexer.peektok()
	tok = mylexer.token()

	while True:
		tok = mylexer.token()

		if mylexer.peektok().type in ('NAME', 'PRINT', 'WHILE'):
			suite.append(parse_stmt())

		if mylexer.peektok().type == 'DEDENT':
			break

	return suite

def parse_expr(left = None, ops = [], comparators = [], times = 0):
	tok = mylexer.peektok()
	# print '***', tok
	if tok.type == 'NAME':
		tok = mylexer.token()
		
		if mylexer.peektok().type in ('LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQA', 'NEQB'):
			if times > 0:
				comparators.append(Name(id = tok.value, ctx = Load()))
			return parse_expr(Name(id = tok.value, ctx = Load()), ops, comparators)
		elif mylexer.peektok().type in ('ASSIGN', 'AUGADD'):
			return Name(id = tok.value, ctx = Store())
		else:
			return Name(id = tok.value, ctx = Load())
	elif tok.type == 'INT':
		tok = mylexer.token()
		
		if mylexer.peektok().type in ('LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQA', 'NEQB'):
			comparators.append(Num(n = tok.value))
			return parse_expr(left, ops, comparators)
		else:
			return Num(n = tok.value)
	elif tok.type == 'MINUS':
		tok = mylexer.token()
		return UnaryOp(op = USub(), operand = parse_expr())
	elif tok.type in ('LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQA', 'NEQB'):
		tok = mylexer.token()
		ops.append(cmp_tools(tok.value))
		times += 1
		expr = parse_expr(left, ops, comparators, times)
		if isinstance(expr, Name) or isinstance(expr, Num):
			comparators.append(expr)
		return Compare(left = left, ops = ops, comparators = comparators)
	else:
		raise Exception('Unexpected Type in Expr')

def cmp_tools(src):
	signs = {'<':Lt(), '>':Gt(), '<=':LtE(), '>=':GtE(), '==':Eq(), '!=':NotEq(), '<>':NotEq()}
	return signs[src]
###############################################################################
# Main
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
			elif isinstance(node, BinOp):
				return "%s + %s" % (_gen(node.left), _gen(node.right))
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

if __name__ == '__main__':
	try:
		txt = sys.stdin.read()
		mylexer = MyLexer()
		mylexer.input(txt)
		tree = parse_module()
		print dump(tree)
		print
		print dump(parse(txt))
		# print generate_c(tree)
	except Exception as e:
		print >> logs, e
		traceback.print_exc(file = logs)

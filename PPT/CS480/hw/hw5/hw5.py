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
		'ASSIGN', 'ADD', 'AUGADD', 'LT', 'COLON', 'COMMA',
		'NEWLINE', 'MINUS', 'LPAREN', 'RPAREN', 'EOF'
	] + keywords.values() 
	
	t_MINUS = r'\-'
	t_ASSIGN = r'\='
	t_ADD = r'\+'
	t_AUGADD = r'\+='
	t_LT = r'\<'
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
		# the initial \n is to simplify indent
		# the final \n is to simplify dedent
		stream = '\n' + stream + '\n' 
		self.lexer.lineno -= 1 # remove first line
		self.lexer.input(stream)
		self.lines = stream.split('\n') # internal
		# print >> logs, 'now lexing...'
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
		# for tok in _tokens:
		# 	print >> logs, tok, # debug
		print >> logs
		_tokens.append(lex.LexToken('EOF', 1, self.lexer.lineno)) # append '$'
		self._tokens = _tokens
		self.tokid = 1 # prepare for token() and peektok()

	def token(self): # eat the next token
		try:
			tok = self._tokens[self.tokid]
			self.tokid += 1
			# print >> logs, tok 
			return tok
		except:
			return None

	def peektok(self): # peek but not eat
		return self._tokens[self.tokid]

###############################################################################
# Parser
'''
module      : stmt+
stmt+       : stmt (epsilon | stmt+)
stmt        : (small_stmt+ | while_stmt) NEWLINE
small_stmt+ : small_stmt (epsilon | small_stmt+)
small_stmt  : assign_stmt | print_stmt
assign_stmt : name assigns
assigns     : ('=' | '+=') decint
print_stmt  : 'print' name
while_stmt  : 'while' name '<' decint ':' suite
suite       : NEWLINE INDENT small_stmt+ DEDENT
'''
def parse_module():
	stmts, tok = parse_stmt()
	
	if tok.type != 'EOF':
		stmts += parse_stmt()

	stmts.pop()
	last = stmts[-1]
	if type(last) is types.ListType:
		stmts.pop()
		stmts += last

	while stmts.count(None) > 0:
		stmts.remove(None)

	return Module(body = stmts)

def parse_stmt():
	stmts = []
	tok = mylexer.peektok()
	
	if tok.type == 'WHILE':
		while_stmt = parse_while_stmt()
		tok = mylexer.token()
		return while_stmt
	else:
		simple_stmt = parse_simple_stmt()
		stmts.append(simple_stmt)
		
		while tok.type == 'NAME' or tok.type == 'PRINT':
			tok = mylexer.peektok()
			simple_stmt = parse_simple_stmt()
			stmts.append(simple_stmt)
		
		while tok.type != 'WHILE':
			if tok.type == 'EOF':
				break
			tok = mylexer.peektok()
		else:
			if tok.type == 'WHILE':
				stmts.append(parse_while_stmt())

		return stmts, tok

def parse_simple_stmt():
	tok, name, sign, expr = mylexer.token(), None, None, None

	if tok.type == 'PRINT':
		values = []
		
		while tok.type != 'NEWLINE' and tok.type != 'EOF':
			tok = mylexer.peektok()
			expr = parse_expr()
			values.append(expr)
			tok = mylexer.token()

		if tok.type == 'NEWLINE':
			return Print(dest = None, values = values, nl = True)
	elif tok.type == 'NAME':
		if mylexer.peektok().type == 'ADD':
			name = parse_expr(Name(id = tok.value, ctx = Load()))
		else:
			name = tok.value

		tok = mylexer.token()
		sign = tok.type
		expr = parse_expr()
		tok = mylexer.token()
		
		while tok.type != 'NEWLINE':
			tok = mylexer.token()
		else:
			if sign == 'AUGADD':
				return AugAssign(target = Name(id = name, ctx = Store()), op = Add(), value = expr)
			elif sign == 'LT':
				if isinstance(name, BinOp):
					return Compare(left = name, ops = [Lt()], comparators = [expr])
				else:
					return Compare(left = Name(id = name, ctx = Load()), ops = [Lt()], comparators = [expr])
			else:
				return Assign(targets = [Name(id = name, ctx = Store())], value = expr)


def parse_while_stmt():
	body = []
	tok = mylexer.peektok()

	if tok.type == 'WHILE':
		tok = mylexer.token()

	test = parse_simple_stmt()

	while tok.type != 'INDENT':
		tok = mylexer.token()

	tok = mylexer.peektok()
	
	while tok.type == 'NAME' or tok.type == 'PRINT':
		body.append(parse_simple_stmt())
		tok = mylexer.peektok()
	
	if tok.type == 'WHILE':
		body.append(parse_while_stmt())
	
	tok = mylexer.peektok()
	
	if tok.type == 'PRINT':
		body.append(parse_simple_stmt())

	while tok.type != 'NEWLINE':
		tok = mylexer.token()

	return While(test = test, body = body, orelse = [])

def parse_expr(left= None, right = None):
	tok = mylexer.token()
	
	if tok.type == 'INT':
		return Num(n = tok.value)
	elif tok.type == 'NAME':
		if mylexer.peektok().type == 'ADD':
			left = Name(id = tok.value, ctx = Load())
			tok = mylexer.peektok()
			tok = mylexer.token()
			tok = mylexer.token()
			right = Name(id = tok.value, ctx = Load())

			if mylexer.peektok().type == 'NEWLINE':
				return BinOp(left = left, op = Add(), right = right)
			else:
				return parse_expr(left, right)
		else:
			return Name(id = tok.value, ctx = Load())
	elif tok.type == 'ADD':
		tok = mylexer.token()

		if right != None:
			left = BinOp(left = left, op = Add(), right = right)

		right = Name(id = tok.value, ctx = Load())
		tok = mylexer.peektok()
		
		if tok.type == 'ADD':
			return parse_expr(left, right)
		else:
			return BinOp(left = left, op = Add(), right = right)

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
		# print dump(tree)
		# print
		# print dump(parse(txt))
		print generate_c(tree)
	except Exception as e:
		print >> logs, e
		traceback.print_exc(file = logs)

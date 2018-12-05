#!/usr/bin/env python
# author: Luan Songjian
# finish date: 2016-01-11
# update date: 2016-01-16

import sys, re, ast
from ast import *

logs  = sys.stderr
target, bound, count = '', 'bound', 0
dict_name = {}

def print_format(nodes, flag):
	fmt, val, d_cnt, s_cnt = '', '', 0, 0
	
	for i in range(len(nodes)):
		if generate_ast_c(nodes[i]).find('||') == -1 and generate_ast_c(nodes[i]).find('&&') == -1 and generate_ast_c(nodes[i]).find('>=') == -1 and generate_ast_c(nodes[i]).find('>') == -1 and generate_ast_c(nodes[i]).find('==') == -1 and generate_ast_c(nodes[i]).find('!=') == -1 and generate_ast_c(nodes[i]).find('<') == -1 and generate_ast_c(nodes[i]).find('<=') == -1 and generate_ast_c(nodes[i]).find('not') == -1:
			if i == len(nodes) - 1: 
				val += generate_ast_c(nodes[i])
			else: 
				val += generate_ast_c(nodes[i])  + ', '
		else:
			if generate_ast_c(nodes[i]).find('?') == -1 and generate_ast_c(nodes[i]).find(':') == -1:
				if i == len(nodes) - 1: 
					val += '(' + generate_ast_c(nodes[i]) + ') ? \"True\" : \"False\"'
				else: 
					val += '(' + generate_ast_c(nodes[i])  + ') ? \"True\" : \"False\", '
			else:
				if i == len(nodes) - 1: 
					val += generate_ast_c(nodes[i])
				else: 
					val += generate_ast_c(nodes[i])  + ', '
	
	lst = val.split(',')

	for item in lst:
		if item.find('True') != -1 or item.find('False') != -1:
			s_cnt += 1

	d_cnt = len(lst) - s_cnt

	if flag == True:
		fmt =  '\"' + '%d ' * d_cnt + '%s ' * s_cnt
	else:
		fmt =  '\"' + '%d ' * d_cnt + '%s ' * s_cnt

	return fmt[: len(fmt) - 1] + '\\n\", ' + val

def assign_format(assigns):
	val = ''
	
	for key in assigns.keys():
		val += key + ', '
		
	return val[ : len(val) - 2]

def temp_format(temps, bound):
	if temps.has_key(bound) == True:
		return bound
	else:
		bound += '_'
		temps[bound] = True;
		return bound

def if_body_format(body):
	val = ''
	
	for item in body:
		val += '\t' + generate_ast_c(item)

	return val

def for_body_format(body, iter):
	val, assign = '', False
	
	for item in body:
		if isinstance(item, Assign):
			if isinstance(item.value, BinOp):
				if generate_ast_c(item.value.left) == iter:
					assign = True
				else:
					assign = False
			else:
				assign = False

		val += '\t' + generate_ast_c(item)

	return val

def if_ops_format(left, ops, comparators):
	lhs, rhs, val = '', '', ''

	for i in range(len(ops) - 1):
		if i == 0:
			lhs = generate_ast_c(left)
			rhs = generate_ast_c(comparators[0])
			val += lhs + ' ' + generate_ast_c(ops[0]) + ' ' + rhs
		else:
			lhs = generate_ast_c(comparators[i])
			rhs = generate_ast_c(comparators[i + 1])
			val += ' && ' + lhs + ' ' + generate_ast_c(ops[i + 1]) + ' ' + rhs

	return val

def generate_ast_c(n):
	if isinstance(n, AST):
		if isinstance(n, Module):
			for body in n.body: return generate_ast_c(body)
		elif isinstance(n, Expr):
			return '%s' % generate_ast_c(n.value)
		elif isinstance(n, AugAssign):
			return '%s %s= %s;\n' % (generate_ast_c(n.target), generate_ast_c(n.op), generate_ast_c(n.value))
		elif isinstance(n, Assign):
			return '\t%s = %s;\n' % (generate_ast_c(n.targets[0]), generate_ast_c(n.value))
		elif isinstance(n, Compare):
			if len(n.ops) == 1:
				return '%s %s %s' % (generate_ast_c(n.left), generate_ast_c(n.ops[0]), generate_ast_c(n.comparators[0]))
			else:
				return '%s' % if_ops_format(n.left, n.ops, n.comparators)
		elif isinstance(n, If):
			return '\tif (%s)\n\t{\n%s\t}\n' % (generate_ast_c(n.test), if_body_format(n.body))
		elif isinstance(n, IfExp):
			return '((%s) ? %s : %s)' % (generate_ast_c(n.test), generate_ast_c(n.body), generate_ast_c(n.orelse))
		elif isinstance(n, BoolOp):
			return '(%s %s %s)' % (generate_ast_c(n.values[0]), generate_ast_c(n.op), generate_ast_c(n.values[1]))
		elif isinstance(n, And):
			return '&&'
		elif isinstance(n, Or):
			return '||'
		elif isinstance(n, For):
			global count, target, bound
			count += 1
			target = generate_ast_c(n.target) + str(count)
			bound = bound + str(count)
			return '\tint %s;\n\tint %s = %s;\n\tfor(%s = 0; %s < %s; %s ++)\n\t{\n\t\t%s = %s;\n%s\t}\n' % (target, bound, generate_ast_c(n.iter), target, target, bound, target, generate_ast_c(n.target), target, for_body_format(n.body, ''))
		elif isinstance(n, Call):
			return '%s' % generate_ast_c(n.args[0])
		elif isinstance(n, Print):
			return '\tprintf(' + print_format(n.values, n.nl) + ');\n'
		elif isinstance(n, UnaryOp):
			if isinstance(n.op, USub):
				return '(-%s)' % generate_ast_c(n.operand)
			elif isinstance(n.op, Not):
				return '(!%s)' % generate_ast_c(n.operand)
			else:
				pass
		elif isinstance(n, BinOp):
			return '(%s %s %s)' % (generate_ast_c(n.left), generate_ast_c(n.op), generate_ast_c(n.right))
		elif isinstance(n, Add):
			return '+'
		elif isinstance(n, Sub):
			return '-'
		elif isinstance(n, Eq):
			return '=='
		elif isinstance(n, NotEq):
			return '!='
		elif isinstance(n, Gt):
			return '>'
		elif isinstance(n, GtE):
			return '>='
		elif isinstance(n, Lt):
			return '<'
		elif isinstance(n, LtE):
			return '<='
		elif isinstance(n, Name):
			if n.id != 'True' and n.id != 'False':
				dict_name[n.id] = True

			if n.id == 'True':
				return '1'
			elif n.id == 'False':
				return '0'
			else:
				return n.id
		elif isinstance(n, Num):
			return '(%s)' % n.n
		else:
			raise Exception('Error in _gen: unrecognized AST node: %s' % ast.dump(n))
	else:
		raise Exception('Error in _gen: unrecognized non-AST of %s: %s' % (str(type(n))[1:-1], str(n)))

if __name__ == "__main__":        
	try:
		print '#include <stdio.h>'
		print '#include <stdlib.h>'
		print
		print 'int main(int argc, char *argv[])'
		print '{'		

		lines = sys.stdin.readlines()
		c_syntax = ''

		for i in range(len(lines)):
			if lines[i].startswith('if') == False and lines[i].startswith('for') == False and lines[i].startswith('\t') == False and lines[i].startswith(' ') == False and lines[i].startswith('\n') == False:
				tree = ast.parse(lines[i])
				generate_ast_c(tree)
				c_syntax = 'int ' + assign_format(dict_name) + ';\n'
			else:
				if lines[i].startswith('if') or lines[i].startswith('for'):
					c_syntax = lines[i]
					j = i + 1;
					while j < len(lines):
						if lines[j].startswith('\t') or lines[j].startswith(' '):
							c_syntax += lines[j]
							j += 1
						else:
							break

					tree = ast.parse(c_syntax)
					generate_ast_c(tree)
					c_syntax = 'int ' + assign_format(dict_name) + ';\n'
		
		if len(dict_name.keys()) > 0:
			print '\t' + c_syntax,
		
		c_syntax = ''

		for i in range(len(lines)):
			if lines[i].startswith('if') == False and lines[i].startswith('for') == False and lines[i].startswith('\t') == False and lines[i].startswith(' ') == False and lines[i].startswith('\n') == False:
				tree = ast.parse(lines[i])
				print '' + generate_ast_c(tree)
			else:
				if lines[i].startswith('if') or lines[i].startswith('for'):
					c_syntax = lines[i]
					j = i + 1;
					while j < len(lines):
						if lines[j].startswith('\t') or lines[j].startswith(' '):
							c_syntax += lines[j]
							j += 1
						else:
							break

					tree = ast.parse(c_syntax)
					print '' + generate_ast_c(tree)

		print '\treturn EXIT_SUCCESS;'
		print '}'
	except Exception, e:
		print e.args[0]
		exit(-1)

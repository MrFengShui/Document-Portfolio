#!/usr/bin/env python
# author: Luan Songjian
# finish date: 2016-01-11
# update date: 2016-01-16

import sys, compiler, re
logs = sys.stderr
from compiler.ast import *

c_syntax = ''
list_location = []
dict_name = {}
dict_assign = {}

def print_format(nodes):
	val = ''

	for i in range(len(nodes)):
		if i == len(nodes) - 1: val += generate_c(nodes[i], False)
		else: val += generate_c(nodes[i], False) + ', '

	fmt =  '\"' + '%d ' * len(nodes) + '\b' + '\\n\", '
	return fmt + val

def assign_format(assigns):
	val = ''
	
	for key in assigns.keys():
		val += key + ', '
		
	return val[ : len(val) - 2]

def for_body_format(body, temp, flag):
	val = ''

	for item in body:
		val += generate_c(item, flag)

	return '\t' + temp + val

def for_format(ctx):
	return ctx.split('for')[1 :]

def content_format(lst):
	ctx = ''

	for item in lst:
		if item.find('for') != -1:
			index = lst.index(item)
			i = 1

			while(lst[index + i][0] == '\t'):
				item += lst[index + i]
				i += 1

			ast = compiler.parse(item)
			ctx += generate_c(ast, False)
		else:
			if item[0] != '\t':
				ast = compiler.parse(item)
				ctx += generate_c(ast, False)

	return ctx
	
def generate_c(n, flag):
	if isinstance(n, Module):
		return ''.join([generate_c(n.node, False)])
	elif isinstance(n, Stmt):
		for node in n.nodes:
			return generate_c(n.nodes[0], False)
	elif isinstance(n, Printnl):
		return '\tprintf(' + print_format(n.nodes) + ');\n'
	elif isinstance(n, AssName):
		dict_assign[n.name] = True
		return '%s' % n.name
	elif isinstance(n, Const):
		return '%d' % n.value
	elif isinstance(n, Name):
		return '%s' % n.name
	elif isinstance(n, UnarySub):
		return '- %s' % generate_c(n.expr, False)
	elif isinstance(n, UnaryAdd):
		return '+ %s' % generate_c(n.expr, False)
	elif isinstance(n, Assign):
		child = n.getChildren()
		
		if flag == False:
			return '\t%s = %s;\n' % (generate_c(child[0], False), generate_c(child[1], False))
		else:
			m = generate_c(child[1], False)
			
			if re.match('[0-9]', m) == None:
				return '\t\t%s = %s_;\n' % (generate_c(child[0], False), generate_c(child[1], False))
			else:
				return '\t\t%s_ = %s;\n' % (generate_c(child[0], False), generate_c(child[1], False))
	elif isinstance(n, Add):
		return '%s + %s' % (generate_c(n.left, False), generate_c(n.right, False))
	elif isinstance(n, Sub):
		return '%s - %s' % (generate_c(n.left, False), generate_c(n.right, False))
	elif isinstance(n, Mul):
		return '%s * %s' % (generate_c(n.left, False), generate_c(n.right, False))
	elif isinstance(n, Div):
		return '%s / %s' % (generate_c(n.left, False), generate_c(n.right, False))
	elif isinstance(n, CallFunc):
		return '%s' % generate_c(n.args[0], False)
	elif isinstance(n, For):
		name, temp, flag = '', '', False

		for body in n.body:
			if isinstance(body.getChildren()[1], Const):
				m, flag = body.getChildren()[0], True

				if isinstance(m, AssName):
					name = m.name
					temp = '\t' + name + '_ = ' + name + ';\n'

				break
		
		if flag == True:
			return '\n\t%s\n\n\tfor(%s = 0; %s < %s; %s ++)\n\t{\n%s\t}\n\n\t%s;\n' % ('int ' + name + '_;', generate_c(n.assign, False), generate_c(n.assign, False), generate_c(n.list, False), generate_c(n.assign, False), for_body_format(n.body, temp, flag), name + ' = ' + name + '_')
		else:
			return '\n\tfor(%s = 0; %s < %s; %s ++)\n\t{\n%s\t}\n\n' % (generate_c(n.assign, False), generate_c(n.assign, False), generate_c(n.list, False), generate_c(n.assign, False), for_body_format(n.body, temp, flag))
	else:
		raise sys.exit('Error in generate_c: unrecognized AST node: %s' % n)

if __name__ == "__main__":        
	try:
		print '#include <stdio.h>'
		print '#include <stdlib.h>'
		print
		print 'int main(int argc, char *argv[])'
		print '{'		

		lst = sys.stdin.readlines()
		c_syntax = content_format(lst)	

		if assign_format(dict_assign) != '':
			print '\tint ' + assign_format(dict_assign) + ';'

		print c_syntax
		print '\treturn EXIT_SUCCESS;'
		print '}'
		
	except Exception, e:
		print e.args[0]
		exit(-1)

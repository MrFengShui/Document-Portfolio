#!/usr/bin/env python

__author__ = "Liang Huang"

'''translate the AST parsed by ast.parse() and generate C code.'''

import sys
logs = sys.stderr
#import compiler
#from compiler.ast import *
import ast # ast.parse, ast.dump
from ast import *
import copy

def generate_c(node):
    variables = {} # var_name -> value
    
    def make_loop_var(s):
        while s in variables:
            s += "_"
        return s
    
    def _gen(node, in_loop=False):
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
            elif isinstance(node, UnaryOp) and isinstance(node.op, USub):
                return "(-%s)" % _gen(node.operand)
            elif isinstance(node, BinOp) and isinstance(node.op, Add):
                return '(%s+%s)' % (_gen(node.left), _gen(node.right))
            elif isinstance(node, Assign):
                line = "%s = %s;" % (_gen(node.targets[0], in_loop),  #pass it in
                                     _gen(node.value))
                variables[node.targets[0].id] = node.value # assigned
                return line
            elif isinstance(node, Name):
                if isinstance(node.ctx, Load): # R-value
                    if node.id not in variables or variables[node.id] is None:
                        raise Exception("undefined variable %s in Python code" % node.id)
                    return node.id
                elif node.id in variables:                    
                    return node.id
                else: # new variable assignment
                    variables[node.id] = None # blank place-holder
                    # do not declare anything in loop!
                    return node.id if in_loop else "int %s" % node.id
            elif isinstance(node, For) and isinstance(node.iter, Call) \
                    and node.iter.func.id == "range":
                
                current_vars = set(variables.keys()) # make a snapshot of current vars

                var_def = _gen(node.target)   # int i
                var_out = _gen(node.target)   # i       
                limit = _gen(node.iter.args[0]) # x in range(x)                
                variables[var_out] = 0
                body = _gen(node.body[0], in_loop=True) # only ONE stmt; TODO: stmt+
                # declare local vars used in the loop body outside of the loop
                declars = "\n".join("int %s;" % x for x in variables.keys() if x not in current_vars) 
                var_in = make_loop_var(node.target.id + "_")
                limit_var = make_loop_var(var_in + "_")
                variables[limit_var] = 0 # can't reuse limit_var, but can reuse loop_var
                return "\n".join([declars,
                                  "int %s = %s;" % (limit_var, limit),
                                  "for (int %s = 0; %s < %s; %s++)" % (var_in,
                                                                       var_in,
                                                                       limit_var,
                                                                       var_in),
                                  "  { %s = %s; %s }" % (var_out, var_in, body)])
            else:
                raise Exception('Error in _gen: unrecognized AST node: %s' % ast.dump(node))
        else:
            raise Exception('Error in _gen: unrecognized non-AST of %s: %s' % (str(type(node))[1:-1], str(node)))

    return _gen(node)

if __name__ == "__main__":        
    variables = set()
    try:
        tree = ast.parse("\n".join(sys.stdin.readlines()))
        print >> logs, ast.dump(tree) # debug
        print generate_c(tree)
    except Exception, e:
        print >> logs, e.args[0]
        exit(-1)


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
    variables = set()
    try:
        tree = ast.parse("\n".join(sys.stdin.readlines()))
        print >> logs, ast.dump(tree) # debug
        print generate_c(tree)
    except Exception, e:
        print >> logs, e.args
        import traceback
        traceback.print_exc()
        exit(-1)


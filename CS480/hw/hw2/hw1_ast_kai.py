#!/usr/bin/env python

'''translate the AST parsed by compiler.parse() and generate C code.
   based on Siek's code, but added assignments and for statement.'''

import sys
logs = sys.stderr
import ast

def generate_c(n):
    declared_variables = set()
    loopvar_count = [0]
    
    def get_loopvar():
        '''finds an unused variable name.'''
        var = "loop_%d" % loopvar_count[0]  # work around for the incompleteness of python's closure
        loopvar_count[0] += 1  
        return var if var not in declared_variables else get_loopvar()

    def get_variables(n):
        '''gets all variables used in the ast node.'''
        if isinstance(n, ast.Module):
            for stmt in n.body:
                get_variables(stmt)
        elif isinstance(n, ast.Print) or \
             isinstance(n, ast.Num) or \
             isinstance(n, ast.UnaryOp) or \
             isinstance(n, ast.BinOp): 
            return
        elif isinstance(n, ast.Name):
            if n.id == "True" or n.id == "False":
                return 
            else:
                declared_variables.add(n.id)
                return
        elif isinstance(n, ast.Assign):
            get_variables(n.targets[0])  
        elif isinstance(n, ast.For):
            get_variables(n.target)
            for stmt in n.body:
                get_variables(stmt)
        else:
            raise sys.exit('Error in generate_c: unrecognized AST node: %s' % n)        
    
    def gen(n):
        if isinstance(n, ast.Module):
            return "\n".join(["#include <stdio.h>",
                              "int main()",
                              "{",
                              "\n".join(["int %s;" % v for v in declared_variables]),
                              "\n".join([gen(stmt) for stmt in n.body]),
                              "return 0;",
                              "}"])
        elif isinstance(n, ast.Print): 
            format_str = " ".join(["%d"] * len(n.values))
            values = ", ".join([gen(v) for v in n.values])
            return "printf(\"%s\\n\", %s);" % (format_str, values)
        elif isinstance(n, ast.Num):
            return '%d' % n.n
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return '(-%s)' % gen(n.operand)
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            left = gen(n.left)
            right = gen(n.right)
            return "%s + %s" % (left, right) 
        elif isinstance(n, ast.Name):
            if n.id == "True" or n.id == "False":
                return str.lower(n.id)
            else:
                assert n.id in declared_variables, "Undeclared variable %s" % n.id
                return n.id
        elif isinstance(n, ast.Assign):
            var = gen(n.targets[0])  # we only allow single variable assignment
            value = gen(n.value)
            return "%s = %s;" % (var, value)
        elif isinstance(n, ast.For):
            loopvar = get_loopvar()
            var = gen(n.target)
            looprange = gen(n.iter.args[0])
            looprange_var = get_loopvar()
            expr = "\n".join(gen(s) for s in n.body)
            return "\n".join([
                "int %s = %s;" % (looprange_var, looprange),
                "for(int %s=0; %s<%s; ++%s){" % (loopvar, loopvar, looprange_var, loopvar),
                "%s = %s;" % (var, loopvar),
                expr,
                "}"])
        else:
            raise sys.exit('Error in generate_c: unrecognized AST node: %s' % n)

    get_variables(n)
    return gen(n)

if __name__ == "__main__":        
    tree = ast.parse("\n".join(sys.stdin.readlines()))
    print >> logs, ast.dump(tree) # debug
    print generate_c(tree)


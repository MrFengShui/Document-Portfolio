#!/usr/bin/env python

__author__ = "James Cross"

import sys
logs = sys.stderr

import ast


def generate_c(node, localvars=None):

    if localvars is None:
        localvars = set()

    if isinstance(node, ast.Module):
        body = '\n'.join([generate_c(stmt, localvars) for stmt in node.body])
        if len(localvars) > 0:
            declarations = '\n'.join(['int {};'.format(v) for v in localvars])
            body = '\n'.join([declarations, body])
        return '\n'.join(
            [
                "#include <stdio.h>",
                "int main()",
                "{", 
                body, 
                "return 0;",
                "}",
            ],
        )
    elif isinstance(node, ast.Print):
        return '\nprintf(" ");\n'.join(
            [
                'printf("%d", {});'.format(generate_c(val, localvars)) 
                for val in node.values
            ],
        ) + '\nprintf("\\n");'
    elif isinstance(node, ast.Num):
        return str(node.n)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return '(-{})'.format(generate_c(node.operand), localvars)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return '{} + {}'.format(
            generate_c(node.left, localvars), 
            generate_c(node.right, localvars),
        )
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Assign):
        name = node.targets[0].id
        localvars.add(name)
        return '{} = {};'.format(
            name,
            generate_c(node.value, localvars),
        )
    elif isinstance(node, ast.For):
        name = node.target.id
        localvars.add(name)        
        mangled = name + '___lkcwfgh'
        localvars.add(mangled)
        end = mangled + '_end'
        localvars.add(end)

        body = '\n'.join([generate_c(stmt, localvars) for stmt in node.body])
        return '\n'.join([
            '{} = {};'.format(
                end, 
                generate_c(node.iter.args[0], localvars),
            ),
            'for ({} = 0; {} < {}; ++{}) {{'.format(
                mangled,
                mangled,
                end,
                mangled,
            ),
            '{} = {};'.format(name, mangled),
            body,
            '}',
        ])

if __name__ == "__main__":        
    try:
        top = ast.parse("\n".join(sys.stdin.readlines()))
        print >> logs, ast.dump(top) # debug
        print generate_c(top)
    except Exception, e:
        print >> logs, e.args[0]
        exit(-1)

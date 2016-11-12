#!/usr/bin/env python2.7

__author__ = 'Liang Huang; James Cross' 

import sys, traceback
logs = sys.stderr

''' P_1.5 grammar:

   module : stmt+
   stmt : (if_stmt | print_stmt) NEWLINE
   print_stmt : "print" expr             
   if_stmt : "if" name ":" suite
   suite : NEWLINE INDENT stmtlist DEDENT
   expr : decint
   name : "True" | "False"
'''

###############################################################################
# Lexer

import ply.lex as lex

def my(self, t=None, v=None, lineno=1):
    self.type, self.value = t, v # return None
    
lex.LexToken.__str__ = lambda self: "(%s, %s)" % (self.type, self.value)
lex.LexToken.__init__ = my


class MyLexer(object):

    keywords = {
        'print' : 'PRINT',
        'if' : 'IF',
        }
    
    tokens = ['INDENT', 'DEDENT',  
              'COLON',
              'INT', 
              'NAME',
              'NEWLINE',
              ] + keywords.values() 
    
    t_COLON = r':'

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
        print >> logs, "now lexing..."
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
        self._tokens = _tokens
        self.tokid = 0 # prepare for token()

    def token(self):
        try:
            self.tokid += 1
            print >> logs, self._tokens[self.tokid]
            return self._tokens[self.tokid]
        except:
            return None

###############################################################################
# Parser

from ast import * # AST node types and dump() function

precedence = (
    ('nonassoc', 'IF'),
    ('nonassoc','PRINT'),
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

def p_stmt(t): # flattens into a list
    '''stmt : print_stmt NEWLINE
            | if_stmt NEWLINE '''
    t[0] = t[1]

def p_print_stmt(t):
    '''print_stmt : PRINT expr'''
    t[0] = Print(values=[t[2]]) # t[2] is a singleton

def p_if_stmt(t):
    '''if_stmt : IF name COLON NEWLINE INDENT stmtlist DEDENT'''
    #  t[0]      1   2          3   4        5     6       7    
    t[0] = If(test=t[2], body=t[6])

def p_bool(t):
    'name : NAME'
    t[0] = Name(id=t[1], ctx=Load())
    
def p_int_expr(t):
    'expr : INT'
    t[0] = Num(n=t[1])

def p_error(t):
    raise Exception("Syntax error (on line %d): '%s'" % (t.lineno, t.value))


import ply.yacc as yacc

def mydump(r):
    if isinstance(r, AST):
        return dump(r)
    elif isinstance(r, list):
        return "[%s]" % (", ".join(map(dump, r)))
    return str(r)

# Format the result message that the parser produces when running in debug mode.
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
        # lhuang hack
        return "%s...%s" % (repr_str[:15], repr_str[-15:]) #'<%s @ 0x%x>' % (type(r).__name__, id(r))


yacc.format_result = myresult
yacc.format_stack_entry = mystack

tokens = MyLexer.tokens # important

yacc.yacc()

###############################################################################
# Main

if __name__ == "__main__":

    try:
        mylexer = MyLexer()
        tree = yacc.parse(sys.stdin.read(), lexer=mylexer, debug=1)
        print >> logs, dump(tree)
        from hw2_liang import generate_c 
        print generate_c(tree)

    except Exception as e:
        print >> logs, e
        traceback.print_exc(file=logs)

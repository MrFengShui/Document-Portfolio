#!/usr/bin/env python2.7

__author__ = 'Liang Huang' 

import sys, traceback
logs = sys.stderr

''' P_0 grammar:

       module : simple_stmt
       simple_stmt : "print" expr NEWLINE
       expr : decint
            | "-" expr
            | "(" expr ")"
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
        }
    
    tokens = ['INDENT', 'DEDENT',  
              'INT', 
              'NEWLINE', 'MINUS', 'LPAREN', 'RPAREN', 'EOF'
              ] + keywords.values() 
    
    t_MINUS = r'\-'
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
        raise Exception("indent error at line %d:\" %s\"" % (t.lexer.lineno, 
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
        _tokens.append(lex.LexToken('EOF', 1, self.lexer.lineno)) # append "$"
        for tok in _tokens[1:]:
            print >> logs, tok, # debug
        print >> logs
        self._tokens = _tokens
        self.tokid = 1 # prepare for token() and peektok()

    def token(self): # eat the next token
        try:
            tok = self._tokens[self.tokid]
            self.tokid += 1
            print >> logs, "eaten %s" % tok
            return tok
        except:
            return None

    def peektok(self): # peek but not eat
        tok = self._tokens[self.tokid]
        print >> logs, "peeking at %s" % tok
        return tok

###############################################################################
# LL(1) Parser

''' P_0 grammar:

       module : simple_stmt
       simple_stmt : "print" expr NEWLINE
       expr : decint
            | "-" expr
            | "(" expr ")"
'''

from ast import * # AST node types and dump() function

def parse_module():
    tok = mylexer.peektok()
    if tok.type == 'PRINT': # peak but can't eat
        stmt = parse_simple_stmt()
        tok = mylexer.token() # try eat $
        if tok.type == "EOF":
            return Module(body=[stmt]) # N.B. should return Module
        else:
            raise Exception("expected EOF, but got %s" % tok)
    else:
        raise Exception("expected print, but got %s" % tok)

def parse_simple_stmt():
    tok = mylexer.token() # eat it!
    if tok.type == 'PRINT':
        expr = parse_expr()
        tok = mylexer.token()
        if tok.type  == "NEWLINE": # try eat newline
            return Print(values=[expr])
        else:
            raise Exception("expected NEWLINE, but got %s" % tok)
    else:
        raise Exception("expected print, but got %s" % tok)

def parse_expr():
    tok = mylexer.token() # eat it!
    if tok.type == "INT":
        return Num(n=tok.value)
    elif tok.type == "MINUS":
        return UnaryOp(op=USub(), operand=parse_expr())
    elif tok.type == "LPAREN":
        expr = parse_expr()
        tok = mylexer.token() # try eat ")"
        if tok.type == "RPAREN": 
            return expr
        else:
            raise Exception("expected ), but got %s" % tok)
    else:
        raise Exception("expected (, -, or int, but got %s" % tok)

###############################################################################

# translate

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
            elif isinstance(node, UnaryOp) and isinstance(node.op, USub):
                return '(-(%s))' % _gen(node.operand)
            else:
                raise Exception('Error in _gen: unrecognized AST node: %s' % dump(node))
        else:
            raise Exception('Error in _gen: unrecognized non-AST of %s: %s' % (str(type(node))[1:-1], str(node)))

    return _gen(node)

###############################################################################
# Main

if __name__ == "__main__":

    try:
        mylexer = MyLexer()
        mylexer.input(sys.stdin.read())
        tree = parse_module()
        print >> logs, dump(tree)
        print generate_c(tree)

    except Exception as e:
        print >> logs, e
        traceback.print_exc(file=logs)

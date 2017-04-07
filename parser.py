from lexer import tokens
from TRS import Operator, Signature

import ply.yacc as yacc


def p_program(p):
    """ program : program statement
                | statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_statement(p):
    """ statement : signature
                  | term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        pass


def p_signature(p):
    """ signature : LPAREN SIGNATURE_KW oplist RPAREN"""
    p[0] = ('signature', Signature(p[3]))


def p_term(p):
    """ term : SYMBOL
             | SYMBOL LPAREN RPAREN
             | SYMBOL LBRACKET RBRACKET
             | SYMBOL LBRACE RBRACE"""

    p[0] = ('term', p[1])


def p_oplist(p):
    """ oplist : operator
                | oplist operator"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_operator(p):
    """ operator : SYMBOL ARITY_KW ARITY"""
    p[0] = Operator(p[1], int(p[3]))


parser = yacc.yacc()


def load_source(filename):
    signature = {}
    rules = {}
    with open(filename) as file:
        result = parser.parse(file.read())
        print result
    return signature, rules


if __name__ == "__main__":
    load_source('test.trs')

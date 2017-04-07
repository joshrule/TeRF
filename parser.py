from lexer import tokens
from TRS import Operator, Signature

import ply.yacc as yacc


def p_program(p):
    """ program : program statement
                | statement"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1]
        p[0].update(p[2])


def p_statement(p):
    """ statement : signature_statement"""
    p[0] = p[1]


def p_signature_statement(p):
    """ signature_statement : SIGNATURE_KW oplist"""
    p[0] = Signature(p[2])


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


def load_source(file):
    signature = {}
    rules = {}
    with open(file) as f:
        result = parser.parse(f.read())
        print result
    return signature, rules


if __name__ == "__main__":
    load_source('test.trs')

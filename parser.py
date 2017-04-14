import ply.yacc as yacc

from lexer import tokens


def p_program(p):
    """ program :
                | program statement"""
    if len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    else:
        p[0] = []


def p_statement(p):
    """ statement : term
                  | rule"""
    p[0] = p[1]


def p_term(p):
    """ term : application
             | variable
             | LPAREN term RPAREN"""
    if len(p) == 2:
        p[0] = ('term', p[1])
    else:
        p[0] = p[2]


def p_application(p):
    """ application : OPERATOR
                    | OPERATOR LBRACKET termlist RBRACKET"""
    if len(p) == 2 or (len(p) == 5 and len(p[3]) == 0):
        p[0] = ('application', p[1], [])
    else:
        p[0] = ('application', p[1], p[3])


def p_variable(p):
    """ variable : VARIABLE"""
    p[0] = ('variable', p[1])


def p_termlist(p):
    """ termlist :
                 | termlist term"""
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_rule(p):
    """ rule : term RULE_KW term"""
    p[0] = ('rule', p[1], p[3])


parser = yacc.yacc()


if __name__ == '__main__':
    with open('test.trs') as f:
        for item in parser.parse(f.read()):
            print item

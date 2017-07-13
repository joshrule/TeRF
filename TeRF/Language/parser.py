from copy import copy
import ply.yacc as yacc

from TeRF.Language.lexer import tokens
from TeRF.Types.Operator import Op
from TeRF.Types.Variable import Var
from TeRF.Types.Application import App
from TeRF.Types.TRS import TRS
from TeRF.Types.Rule import R
from TeRF.Types.Signature import Signature


def p_program(p):
    """ program :
                | program statement"""
    if len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    else:
        p[0] = []


def p_statement(p):
    """ statement : rule SEMICOLON
                  | assumption SEMICOLON
                  | signature SEMICOLON
                  | termlisttop SEMICOLON"""
    if p[1][0] not in ['rule', 'signature', 'assumption']:
        p[0] = builder(p[1])
    else:
        p[0] = p[1]


def p_rule(p):
    """ rule : termlisttop RULE_KW rhs"""
    p[0] = ('rule', builder(p[1]), p[3])


def p_rhs(p):
    """ rhs : termlisttop
            | rhs PIPE termlisttop"""
    if len(p) == 2:
        p[0] = [builder(p[1])]
    else:
        p[0] = p[1] + [builder(p[3])]


def p_termlisttop(p):
    """ termlisttop : term
                    | termlisttop term"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_term(p):
    """ term : application
             | variable
             | LPAREN termlist RPAREN"""
    if len(p) == 2:
        p[0] = ('term', p[1])
    else:
        p[0] = builder(p[2])


def p_termlist(p):
    """ termlist : term
                 | termlist term"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_assumption(p):
    """ assumption : ASSUME_KW STRING"""
    p[0] = ('assumption', p[2][1:-1])


def p_signature(p):
    """ signature : SIGNATURE_KW atomlist"""
    p[0] = ('signature', p[2])


def p_atomlist(p):
    """ atomlist : atom
                 | atomlist atom"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]


def p_atom(p):
    """ atom : variable
             | OPERATOR ARITY"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operator', p[1], p[2][1:])


def p_application(p):
    """ application : OPERATOR
                    | OPERATOR LBRACKET RBRACKET
                    | OPERATOR LBRACKET termlist RBRACKET"""
    if len(p) == 2 or len(p) == 4:
        p[0] = ('application', p[1], [])
    else:
        p[0] = ('application', p[1], p[3])


def p_variable(p):
    """ variable : VARIABLE"""
    p[0] = ('variable', p[1])


def builder(terms):
    if len(terms) == 1:
        return terms[0]
    else:
        return ('term', ('application', '.', [builder(terms[:-1]), terms[-1]]))


def p_error(p):
    if p is None:
        print 'TeRF Parse Error! Unexpected EOF'
    else:
        print 'TeRF Parse Error! What do I do with {}?'.format(p)
        parser.errok()


parser = yacc.yacc()


def make_trs(ss, trs=None, path=None):
    trs = TRS() if trs is None else trs
    for s in ss:
        if s[0] == 'rule':
            add_rule(trs, s[1], s[2])
        elif s[0] == 'signature':
            add_signature(trs, s[1])
        elif s[0] == 'assumption':
            add_assumption(trs, s[1], path=path)
    return trs


def add_assumption(trs, s, path=None):
    s += '.terf' if len(s) <= 5 or s[-5:] != '.terf' else ''
    if path is None:
        path = ['./']
    for lib in path:
        try:
            filename = lib + s
            with open(filename) as file:
                ss = parser.parse(file.read())
                return make_trs(ss, trs=trs, path=path)
        except IOError:
            pass
    print 'Can\'t find {}'.format(s)


def add_signature(trs, s):
    for t in s:
        if t[0] == 'operator':
            trs.signature.add(Op(t[1], int(t[2])))


def add_rule(trs, lhst, rhsts):
    sig = copy(trs.signature)
    lhs = make_term(lhst[1], signature=sig)
    rhs = [make_term(t[1], signature=sig) for t in rhsts]
    trs.signature |= sig.operators
    trs[len(trs)] = R(lhs, rhs)


def make_term(t, signature=None):
    if signature is None:
        signature = Signature()

    if t[0] == 'variable':
        name = t[1][:-1]
        for v in signature.variables:
            if v.name == name:
                return v
        var = Var(name) if name != '' else Var()
        signature.add(var)
        return var

    if t[0] == 'application':
        head = Op(t[1], len(t[2]))
        for o in signature.operators:
            if o.name == t[1] and o.arity == len(t[2]):
                head = o
        signature.add(head)
        body = []
        for part in t[2]:
            term = make_term(part[1], signature=signature)
            body.append(term)
        return App(head, body)


def load_source(filename, path=None):
    with open(filename) as file:
        ss = parser.parse(file.read())
        trs = make_trs(ss, path=path)
        terms = [make_term(s[1], signature=copy(trs.signature))
                 for s in ss if s[0] == 'term']
        return trs, terms


if __name__ == '__main__':
    with open('library/README.terf') as file:
        ss = [s for s in parser.parse(file.read())]
        for statement in ss:
            print statement

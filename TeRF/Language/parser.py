import ply.yacc as yacc
from TeRF.Language.lexer import tokens
from TeRF.Types.Operator import Op
from TeRF.Types.Variable import Var
from TeRF.Types.Application import App
from TeRF.Types.TRS import TRS
from TeRF.Types.Rule import R


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
    if trs is None:
        trs = TRS([])
    for s in ss:
        if s[0] == 'rule':
            add_rule(trs, s[1], s[2])
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


def add_rule(trs, lhst, rhsts):
    scope = set()
    lhs = make_term(lhst[1], scope=scope, trs=trs)
    rhs = [make_term(t[1], scope=scope, trs=trs) for t in rhsts]
    trs[len(trs)] = R(lhs, rhs)


def make_term(t, trs=None, scope=None):
    scope = set() if scope is None else scope
    if t[0] == 'variable':
        return make_variable(t, scope, trs=trs)
    if t[0] == 'application':
        return make_application(t, scope, trs=trs)


def make_variable(t, scope, trs=None):
    name = t[1][:-1]
    for v in scope:
        if name == v.name:
            return v
    var = Var(name) if name != '' else Var()
    scope.add(var)
    return var


def make_application(t, scope, trs=None):
    head = Op(t[1], len(t[2]))
    body = [make_term(b[1], scope=scope, trs=trs) for b in t[2]]
    return App(head, body)


def load_string(string, path=None):
        ss = parser.parse(string)
        trs = make_trs(ss, path=path)
        scope = set()
        terms = [make_term(s[1], scope=scope) for s in ss if s[0] == 'term']
        return trs, terms


def load_source(filename, path=None):
    with open(filename) as f:
        return load_string(f.read(), path=path)


if __name__ == '__main__':
    with open('lib/README.terf') as file:
        ss = [s for s in parser.parse(file.read())]
        for statement in ss:
            print statement

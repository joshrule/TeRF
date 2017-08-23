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


def make_trs(ss, trs=None, path=None, signature=None):
    trs = TRS() if trs is None else trs
    for s in ss:
        if s[0] == 'rule':
            add_rule(trs, s[1], s[2], signature=signature)
        elif s[0] == 'signature':
            add_signature(trs, s[1], signature=signature)
        elif s[0] == 'assumption':
            add_assumption(trs, s[1], path=path, signature=signature)
    return trs


def add_assumption(trs, s, path=None, signature=None):
    s += '.terf' if len(s) <= 5 or s[-5:] != '.terf' else ''
    if path is None:
        path = ['./']
    for lib in path:
        try:
            filename = lib + s
            with open(filename) as file:
                ss = parser.parse(file.read())
                return make_trs(ss, trs=trs, path=path, signature=signature)
        except IOError:
            pass
    print 'Can\'t find {}'.format(s)


def add_signature(trs, s, signature=None):
    # print 'adding signature'
    for t in s:
        if t[0] == 'operator' and trs.signature.find(t[1], int(t[2])) is None:
            if signature is not None and signature.find(t[1], int(t[2])):
                # print 'building signature by adding', t[1], int(t[2])
                trs.signature.add(signature.find(t[1], int(t[2])))
            else:
                trs.signature.add(Op(t[1], int(t[2])))


def add_rule(trs, lhst, rhsts, signature=None):
    vars = trs.signature.variables
    lhs = make_term(lhst[1], trs=trs, signature=signature)
    rhs = [make_term(t[1], trs=trs, signature=signature) for t in rhsts]
    trs.signature.replace_vars(vars)
    trs[len(trs)] = R(lhs, rhs)


def make_term(t, trs=None, signature=None):
    if t[0] == 'variable':
        name = t[1][:-1]
        if trs is not None:
            for v in trs.signature.variables:
                if v.name == name:
                    return v
        if signature is not None:
            for v in signature.variables:
                if v.name == name:
                    return v
        var = Var(name) if name != '' else Var()
        if trs is not None:
            trs.signature.add(var)
        return var

    if t[0] == 'application':
        # print 'looking for', t[1], len(t[2])
        if trs is not None and trs.signature.find(t[1], len(t[2])):
            # print 'checking trs,', trs.signature
            head = trs.signature.find(t[1], len(t[2]))
        elif signature is not None and signature.find(t[1], len(t[2])):
            # print 'checking signature,', signature
            head = signature.find(t[1], len(t[2]))
        else:
            # print 'did not find it'
            head = Op(t[1], len(t[2]))
        if trs is not None:
            trs.signature.add(head)
        elif signature is not None:
            signature.add(head)
        body = []
        for part in t[2]:
            term = make_term(part[1], trs, signature)
            body.append(term)
        return App(head, body)


def load_source(filename, path=None, signature=None):
    with open(filename) as file:
        ss = parser.parse(file.read())
        trs = make_trs(ss, path=path, signature=signature)
        terms = [make_term(s[1], signature=trs.signature.copy())
                 for s in ss if s[0] == 'term']
        return trs, terms


if __name__ == '__main__':
    with open('lib/README.terf') as file:
        ss = [s for s in parser.parse(file.read())]
        for statement in ss:
            print statement

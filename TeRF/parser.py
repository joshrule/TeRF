import ply.yacc as yacc

from TeRF.lexer import tokens
from TeRF.TRS import Operator, Variable, Application, RewriteRule, TRS


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
                  | signature SEMICOLON
                  | termlisttop SEMICOLON"""
    if p[1][0] != 'rule' and p[1][0] != 'signature':
        p[0] = builder(p[1])
    else:
        p[0] = p[1]


def p_rule(p):
    """ rule : termlisttop RULE_KW termlisttop"""
    p[0] = ('rule', builder(p[1]), builder(p[3]))


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


def make_trs(ss):
    trs = TRS()
    for s in ss:
        if s[0] == 'rule':
            trs = add_rule(trs, s[1], s[2])
        elif s[0] == 'signature':
            trs = add_signature(trs, s[1])
    return trs


def add_signature(trs, s):
    for t in s:
        if t[0] == 'operator':
            trs.operators.add(Operator(t[1], int(t[2])))
        else:
            name = t[1][:-1]
            if name not in [v.name for v in trs.variables]:
                trs.variables.add(Variable(name))
    return trs


def add_rule(trs, t1, t2):
    lhs, trs = make_term(t1[1], trs=trs)
    rhs, trs = make_term(t2[1], trs=trs)
    return trs.add_rule(RewriteRule(lhs, rhs))


def make_term(t, trs=None):
    if t[0] == 'variable':
        name = t[1][:-1]
        if trs is not None:
            for v in trs.variables:
                if v.name == name:
                    return v, trs
            var = Variable(name)
            return var, trs.add_var(var)
        return Variable(name)
    
    elif t[0] == 'application':
        head = Operator(t[1], len(t[2]))
        if trs is not None:
            trs.operators.add(head)
            body = []
            for part in t[2]:
                term, trs = make_term(part[1], trs=trs)
                body.append(term)
            term = Application(head, body)
            return term, trs
        return Application(head, [make_term(part[1]) for part in t[2]])


def load_source(filename):
    with open(filename) as file:
        ss = parser.parse(file.read())
    terms = [make_term(s[1], {})[0] for s in ss if s[0] == 'term']
    return make_trs(ss), terms


if __name__ == '__main__':
    with open('test.trs') as file:
        ss = [s for s in parser.parse(file.read())]
        for statement in ss:
            print statement

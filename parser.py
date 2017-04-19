import ply.yacc as yacc

from lexer import tokens
from TRS import Operator, Variable, Application, RewriteRule, TRS


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
                  | termlisttop SEMICOLON"""
    if p[1][0] != 'rule':
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
    rules = [make_rule(s[1], s[2], {}) for s in ss if s[0] == 'rule']
    operators = {op for rule in rules for op in rule.operators}
    for operator in operators:
        trs.add_operator(operator)
    for rule in rules:
        trs.add_rule(rule)
    return trs


def make_rule(t1, t2, env):
    lhs, env = make_term(t1[1], env)
    rhs, env = make_term(t2[1], env)
    return RewriteRule(lhs, rhs)


def make_term(t, env):
    if t[0] == 'variable':
        if t[1][:-1] in env:
            oldvar = env[t[1][:-1]]
            var = Variable(oldvar.name, oldvar.identity)
            return var, env
        else:
            var = Variable(t[1][:-1])
            env[var.name] = var
            return var, env
    elif t[0] == 'application':
        body = []
        for part in t[2]:
            term, env = make_term(part[1], env)
            body.append(term)
        return Application(Operator(t[1], len(t[2])),
                           body), env


def load_source(filename):
    with open(filename) as file:
        ss = parser.parse(file.read())
    terms = [make_term(s[1], {})[0] for s in ss if s[0] == 'term']
    return make_trs(ss), terms


if __name__ == '__main__':
    with open('test.trs') as file:
        for statement in parser.parse(file.read()):
            print statement

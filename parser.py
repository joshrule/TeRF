import ply.yacc as yacc

from lexer import tokens
from TRS import TRS, Variable, Application, Operator, RewriteRule


def p_program(p):
    """ program : program statement
                | statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_statement(p):
    """ statement : term
                  | rule"""
    p[0] = p[1]


def p_term(p):
    """ term : application
             | variable"""
    p[0] = ('term', p[1])


def p_application(p):
    """ application : OPERATOR
                    | OPERATOR LBRACKET termlist RBRACKET"""
    if len(p) == 2 or len(p[3]) == 0:
        p[0] = ('application', p[1], [])
    else:
        p[0] = ('application', p[1], p[3])


def p_vterm(p):
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


if __name__ == "__main__":
    trs, terms = load_source('test.trs')
    print trs
    for term in terms:
        print
        print '{} -*-> {}'.format(term, trs.eval(term, steps=10))

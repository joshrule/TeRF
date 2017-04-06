import ply.lex as lex

tokens = ['COMMENT']
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


# track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print('Illegal character %s' % t.value[0])
    t.lexer.skip[1]


lexer = lex.lex()

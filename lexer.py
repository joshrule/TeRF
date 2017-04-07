import ply.lex as lex

tokens = ['SYMBOL', 'ARITY', 'ARITY_KW']

reserved = {
    'signature': 'SIGNATURE_KW'
}
tokens += reserved.values()

t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


def t_ARITY_KW(t):
    r'/'
    return t


def t_ARITY(t):
    r'[0-9]+'
    return t


def t_SYMBOL(t):
    r'([a-zA-Z0-9_\.\-\$\*\@\?]+)'

    if t.value in reserved:
        t.type = reserved[t.value]

    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print('Illegal character %s' % t.value[0])
    t.lexer.skip[1]


lexer = lex.lex()


def lex_file(file):
    with open(file) as f:
        lexer.input(f.read())
        for token in lexer:
            print token


if __name__ == "__main__":
    lex_file('test.trs')

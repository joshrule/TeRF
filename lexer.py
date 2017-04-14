import ply.lex as lex

# What kinds of things are in TRSs?
# - Terms
#   - Variables "x_"
#   - Applications of Operators to Terms x[x_, ABC]
# - Rewrite Rules "lhs = rhs"
# - Comments "# comment"

tokens = ['VARIABLE',
          'OPERATOR',
          'RULE_KW',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'SEMICOLON']

"""the syntax for variables

Variables are strings ending in _. They may not have whitespace,
brackets, parentheses, #, ;, nor =.
"""
t_VARIABLE = r'([^\s#\[\]\(\)=;])*_(?=[\s#\[\]\(\);])'

"""the syntax for operators

Operators are strings *not* ending in _. They may not have whitespace, commas,
#, brackets, nor the -> combination.
"""
t_OPERATOR = r'([^\s#\[\]\(\)=;])*' + \
             r'[^_\s#\[\]\(\)=;](?=[\s#\[\]\(\);])'

t_RULE_KW = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'

t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print('Illegal character %s' % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


if __name__ == "__main__":
    with open('test.trs') as f:
        lexer.input(f.read())
        for token in lexer:
            print token

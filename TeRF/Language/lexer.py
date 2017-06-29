"""
A Lexer for Term Rewriting Systems (TRSs)

What kinds of things are in TRSs?
- Terms
  - Variables "x_"
  - Applications of Operators to Terms
    - T[x_ ABC]
    - (x_ ABC) (i.e. .[x_ ABC])
    - x_ ABC (i.e. .[x_ ABC])
- Rules
  - Deterministic "lhs = rhs"
  - Non-Deterministic "lhs = rhs1 | rhs2 | ..."
- Assumptions "assume lists.terf"
- Comments "# comment"
- Signatures "signature X/0 ./2"
"""
import ply.lex as lex


reserved = {
    'signature': 'SIGNATURE_KW',
    'assume': 'ASSUME_KW'
}


tokens = ['VARIABLE',
          'OPERATOR',
          'STRING',
          'ARITY',
          'RULE_KW',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'PIPE',
          'SEMICOLON'] + list(reserved.values())


def t_VARIABLE(t):
    r'([^\s\#\[\]\(\)=;/\|\'\"])*_(?=[\s\#\[\]\(\);\|])'
    t.type = reserved.get(t.value, 'VARIABLE')  # Check for reserved words
    return t


def t_OPERATOR(t):
    r'([^\s\#\[\]\(\)=;/\|\'\"])*[^_\s\#\[\]\(\)=;/\|\'\"](?=[\s\#\[\]\(\);/\|])'
    t.type = reserved.get(t.value, 'OPERATOR')  # Check for reserved words
    return t


def t_STRING(t):
    r'\'.*\'|\".+\"'
    t.type = reserved.get(t.value, 'STRING')  # Check for reserved words
    return t


t_ARITY = r'/(\d)+'
t_RULE_KW = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_PIPE = r'\|'
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
    with open('library/README.terf') as f:
        lexer.input(f.read())
        for token in lexer:
            print token

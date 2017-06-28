"""
A Lexer for Term Rewriting Systems (TRSs)

What kinds of things are in TRSs?
- Terms
  - Variables "x_"
  - Applications of Operators to Terms
     - T[x_, ABC]
     - (x_ ABC) (i.e. .[x_, ABC])
- Rewrite Rules "lhs = rhs" or "lhs = rhs1 | rhs2 | ..."
- Comments "# comment"
- Signatures "signature X/0 y_"
"""
import ply.lex as lex


reserved = {
   'signature': 'SIGNATURE_KW'
}


tokens = ['VARIABLE',
          'OPERATOR',
          'ARITY',
          'RULE_KW',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'PIPE',
          'SEMICOLON'] + list(reserved.values())


def t_VARIABLE(t):
    r'([^\s\#\[\]\(\)=;/\|])*_(?=[\s\#\[\]\(\);\|])'
    t.type = reserved.get(t.value, 'VARIABLE')  # Check for reserved words
    return t


def t_OPERATOR(t):
    r'([^\s\#\[\]\(\)=;/\|])*[^_\s\#\[\]\(\)=;/\|](?=[\s\#\[\]\(\);/\|])'
    t.type = reserved.get(t.value, 'OPERATOR')  # Check for reserved words
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
    with open('test.trs') as f:
        lexer.input(f.read())
        for token in lexer:
            print token

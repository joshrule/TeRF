from lexer import lexer
# from lexer import tokens
# import ply.yacc as yacc

# parser = yacc.yacc()


def load_source(file):
    with open(file) as f:
        lexer.input(f.read())
        for token in lexer:
            print token


if __name__ == "__main__":
    load_source('test.trs')

"""TeRF: a Term Rewriting Framework

Usage:
    terf [-ht] [--batch=<filename>] [--print=<level>] [--steps=<N>]

Options:
    -h --help           Show this message
    -t --trace          Trace evaluations
    --batch=<filename>  Process <filename> in batch mode.
    --print=<int>       how to print terms [default: 0].
    --steps=<int>       maximum execution steps for each term. [default: 1000]

REPL mode:
  The following commands are availabile in REPL mode:

   >> <lhs> = <rhs>                 # add the deterministic rule <lhs> = <rhs>
   >> <lhs> = <rhs1> | <rhs2> | ... # add a non-deterministic rule
   >> <term>                        # evaluate the term under the current TRS
   >> quit                          # exit the REPL
   >> exit                          # exit the REPL
   >> ^D                            # exit the REPL
   >> show                          # print the current TRS
   >> del(ete) op(erator) <op_name> # delete operator <op_name> and its rules
   >> del(ete) rule <rule_number>   # delete rule <rule_number>
   >> clear                         # reset the TRS
   >> save <filename>               # save the current TRS to <filename>
   >> assume <filename>             # run the statements in <filename>
   >> canon(ical) <term>            # print the canonical form of <term>
   >> pretty <term>                 # pretty-print <term>
   >> paren(s|thesized) <term>      # print <term> with full parentheses
   >> tree <term>                   # print <term> as a tree
   >> generate                      # generate a new term and assign it a name
"""

from TeRF.Language.parser import parser, load_source, make_term
from TeRF.Language.parser import add_signature, add_rule
from TeRF.Types import Op, App, TRS, R, Sig

from docopt import docopt
from pptree import print_tree
import re


def batch(filename, verbosity, count, trace):
    trs, terms = load_source(filename)
    print 'TRS:'
    print show_trs(trs)
    print '\nEvaluations:'
    for term in terms:
        evaled = term.rewrite(trs, max_steps=count, trace=trace)
        if verbosity >= 0:
            if trace:
                print '\n  {}'.format(term.pretty_print(2*verbosity))
                for t in evaled[1:]:
                    print '  = {}'.format(t.pretty_print(2*verbosity))
            else:
                print '\n  {} = {}'.format(term.pretty_print(2*verbosity),
                                           evaled.pretty_print(2*verbosity))
        else:
            if trace:
                print '\n  {}'.format(term)
                for t in evaled[1:]:
                    print '  = {}'.format(t)
            else:
                print '\n  {} = {}'.format(term, evaled)


def repl(verbosity, count, trace):
    trs = TRS()
    while True:
        try:
            statements = [s.strip() for s in repl_read().split(';') if s != '']
            for statement in statements:
                output, new_ss = repl_eval(trs, statement,
                                           verbosity, count, trace)
                if output != '' and output is not None:
                    print output
                statements += new_ss
        except EOFError:
            break


def repl_read():
    try:
        return raw_input('>> ') + ';'
    except NameError:
        return input('>> ') + ';'


def repl_eval(trs, statement, verbosity, count, trace):
    quit = re.compile('quit')
    exit = re.compile('exit')
    help = re.compile('help')
    clear = re.compile('clear')
    show = re.compile('show')
    delete = re.compile('del(ete)?\s+' +
                        '(?P<type>(rule|op(erator)?))\s+(?P<obj>\S+)')
    save = re.compile('save\s+(?P<filename>\S+)')
    load = re.compile('assume\s+(?P<filename>\S+)')
    canon = re.compile('canon(ical)?\s+(?P<term>.+)')
    pretty = re.compile('pretty\s+(?P<term>.+)')
    parens = re.compile('paren(s|thesized)?\s+(?P<term>.+)')
    generate = re.compile('generate')
    tree = re.compile('tree\s+(?P<term>.+)')
    
    if quit.match(statement) or exit.match(statement):
        raise EOFError
    if show.match(statement):
        return show_trs(trs), []
    if help.match(statement):
        return __doc__, []
    if clear.match(statement):
        trs.operators, trs.rules = set(), []
        return None, []
    if delete.match(statement):
        delete_from_trs(trs,
                        delete.match(statement).group('type'),
                        delete.match(statement).group('obj'))
        return None, []
    if save.match(statement):
        save_trs(trs, save.match(statement).group('filename'))
        return None, []
    if load.match(statement):
        return None, load_file(load.match(statement).group('filename'))
    if canon.match(statement):
        return print_term(canon.match(statement).group('term'), 'canon'), []
    if pretty.match(statement):
        return print_term(pretty.match(statement).group('term'), 'pretty'), []
    if parens.match(statement):
        return print_term(parens.match(statement).group('term'), 'parens'), []
    if generate.match(statement):
        rule = make_a_named_term(trs)
        return None, [str(rule), 'show']
    if tree.match(statement):
        parse = parser.parse(tree.match(statement).group('term') + ';')[0]
        if parse[0] == 'term':
            term = make_term(parse[1])
            return print_tree(term, childattr='body'), []
        return None, []
    else:
        words = process_statement(trs, statement, verbosity, count, trace)
        return words, []


def make_a_named_term(trs):
    lhs = App(Op(), [])
    rhs = [Sig(trs.operators).sample_term(invent=False)]
    return R(lhs, rhs)


def show_trs(trs):
    operators = ', '.join(o.name + '/' + str(o.arity) for o in trs.operators)
    rules = '\n'.join('{:d}: {}'.format(i, rule)
                      for i, rule in enumerate(trs.rules))
    return operators + '\n' + rules


def delete_from_trs(trs, type, obj):
    if type == 'rule':
        trs.del_rule(int(obj))
        return trs

    try:
        op = [op for op in trs.operators if op.name == obj][0]
        trs.del_op(op)
    except IndexError:
        pass
    return trs


def save_trs(trs, filename):
    with open(filename, 'w') as f:
        f.write(';\n'.join([str(rule) for rule in trs.rules])+';\n')


def load_file(filename):
    statements = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                statements += [s.strip() for s in line.strip().split(';')
                               if s != '']
            return statements
    except IOError:
        print 'Can\'t find {}'.format(filename)
        return []


def print_term(term, how):
    s = parser.parse(term + ';')[0]
    if s[0] != 'term':
        return ''
    term = make_term(s[1])
    if how == 'canon':
        return str(term)
    if how == 'pretty':
        return term.pretty_print(verbose=0)
    if how == 'parens':
        return term.pretty_print(verbose=2)


def process_statement(trs, statement, verbosity, count, trace):
    s = parser.parse(statement + ';')[0]
    if s[0] == 'rule':
        add_rule(trs, s[1], s[2])
        return ''
    elif s[0] == 'term':
        term = make_term(s[1])
        evaled = term.rewrite(trs, max_steps=count, trace=trace)
        if verbosity >= 0:
            if trace:
                return '\n'.join(t.pretty_print(2*verbosity)
                                 for t in evaled)
            else:
                return evaled.pretty_print(2*verbosity)
        else:
            if trace:
                return '\n'.join(str(e) for e in evaled)
            else:
                return evaled
    elif s[0] == 'signature':
        add_signature(trs, s[1])
    else:
        return 'Oops! ' + str(s)


def main():
    arguments = docopt(__doc__, version="terf 0.0.1")
    try:
        trace = arguments['--trace']
    except KeyError:
        trace = False
    if arguments['--batch']:
        batch(arguments['--batch'],
              int(arguments['--print']),
              int(arguments['--steps']),
              trace)
    else:
        repl(int(arguments['--print']),
             int(arguments['--steps']),
             trace)


if __name__ == "__main__":
    main()

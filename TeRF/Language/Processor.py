"""TeRF: a Term Rewriting Framework

Usage:
    terf [-ht] [--print=<level>] [--steps=<N>] [--path=<dir>] [--strategy=<name>] [--output=<output>] [<filename>]

Options:
    -h --help            Show this message.
    -t --trace           Trace evaluations.
    --print=<int>        how to print terms. [default: 0].
    --steps=<int>        maximum execution steps for each term. [default: 1000]
    --path=<dir>         where the library is located. [default: ./]
    --strategy=<name>    what evaluation strategy ('normal', 'eager') to use
                         [default: 'eager']
    --output=<output>    print 'all' evaluations or just 'one' [default: 'one']

Batch mode:
  Include a <filename> as the last argument to run terf in batch mode

REPL mode:
  The following commands are availabile in REPL mode:

   >> <lhs> = <rhs>                 # add the deterministic rule <lhs> = <rhs>
   >> <lhs> = <rhs1> | <rhs2> | ... # add a non-deterministic rule
   >> <term>                        # evaluate the term under the current TRS
   >> signature [<name>/<arity>]+   # add the name/arity pairs as operators
   >> assume <filename>             # run the statements in <filename>
   >> quit                          # exit the REPL
   >> exit                          # exit the REPL
   >> ^D                            # exit the REPL
   >> show                          # print the current TRS
   >> del(ete) op(erator) <op_name> # delete operator <op_name> and its rules
   >> del(ete) rule <rule_number>   # delete rule <rule_number>
   >> clear                         # reset the TRS
   >> save <filename>               # save the current TRS to <filename>
   >> canon(ical) <term>            # print the canonical form of <term>
   >> pretty <term>                 # pretty-print <term>
   >> paren(s|thesized) <term>      # print <term> with full parentheses
   >> generate                      # generate a new term and assign it a name
"""

import docopt
import re
import TeRF.Language.parser as p
from TeRF.Types.Operator import Op
from TeRF.Types.Application import App
from TeRF.Types.TRS import TRS
from TeRF.Types.Rule import R
from TeRF.Types.Signature import SignatureError


def batch(filename, verbosity, count, trace, path, strategy, output):
    trs, terms = p.load_source(filename, path=path)
    print 'TRS:'
    print show_trs(trs)
    print '\nEvaluations:'
    for term in terms:
        evaled = term.rewrite(trs, max_steps=count, type=output, trace=trace,
                              strategy=strategy, states=['normal'])
        if output == 'all':
            if verbosity >= 0:
                for i, t in enumerate(set(evaled)):
                    print '{:d}: {}'.format(i, t.pretty_print(2*verbosity))
            else:
                for i, t in enumerate(set(evaled)):
                    print '{:d}: {}'.format(i, t)
        else:
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


def repl(verbosity, count, trace, path, strategy, output):
    trs = TRS()
    while True:
        try:
            statements = [s.strip() for s in repl_read().split(';') if s != '']
            for statement in statements:
                out, new_ss = repl_eval(trs, statement, verbosity,
                                        count, trace, path, strategy, output)
                if out != '' and out is not None:
                    print out
                statements += new_ss
        except EOFError:
            break


def repl_read():
    try:
        return raw_input('>> ') + ';'
    except NameError:
        return input('>> ') + ';'


def repl_eval(trs, statement, verbosity, count, trace, path, strategy, output):
    quit = re.compile('quit')
    exit = re.compile('exit')
    help = re.compile('help')
    clear = re.compile('clear')
    show = re.compile('show')
    delete = re.compile('del(ete)?\s+' +
                        '(?P<type>(rule|op(erator)?))\s+(?P<obj>\S+)')
    save = re.compile('save\s+(?P<filename>\S+)')
    canon = re.compile('canon(ical)?\s+(?P<term>.+)')
    pretty = re.compile('pretty\s+(?P<term>.+)')
    parens = re.compile('paren(s|thesized)?\s+(?P<term>.+)')
    generate = re.compile('generate')

    if quit.match(statement) or exit.match(statement):
        raise EOFError
    if show.match(statement):
        return show_trs(trs), []
    if help.match(statement):
        return __doc__, []
    if clear.match(statement):
        trs.clear()
        return None, []
    if delete.match(statement):
        delete_from_trs(trs,
                        delete.match(statement).group('type'),
                        delete.match(statement).group('obj'))
        return None, []
    if save.match(statement):
        trs.save(save.match(statement).group('filename'))
        return None, []
    if canon.match(statement):
        return print_term(canon.match(statement).group('term'), 'canon'), []
    if pretty.match(statement):
        return print_term(pretty.match(statement).group('term'), 'pretty'), []
    if parens.match(statement):
        return print_term(parens.match(statement).group('term'), 'parens'), []
    if generate.match(statement):
        rule = make_a_named_term(trs)
        if rule is not None:
            return None, [str(rule), 'show']
        return 'cannot invent term -- no terminals?', []
    # TODO: add a tree statement to print trees
    else:
        words = process_statement(trs, statement, verbosity, count,
                                  trace, path=path, strategy=strategy,
                                  output=output)
        return words, []


def make_a_named_term(trs):
    try:
        lhs = App(Op(), [])
        rhs = [trs.signature.sample_term(invent=False)]
        return R(lhs, rhs)
    except SignatureError:
        return None


def show_trs(trs):
    operators = ', '.join(str(s) for s in trs.signature)
    rules = '\n'.join('{:d}: {}'.format(i, rule)
                      for i, rule in enumerate(trs))
    return operators + '\n' + rules


def delete_from_trs(trs, type, obj):
    if type == 'rule':
        del trs[int(obj)]
        return trs

    try:
        op = [op for op in trs.signature if op.name == obj][0]
        trs.signature.discard(op)
    except IndexError:
        pass
    return trs


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
    s = p.parser.parse(term + ';')[0]
    if s[0] != 'term':
        return ''
    term = p.make_term(s[1])
    if how == 'canon':
        return str(term)
    if how == 'pretty':
        return term.pretty_print(verbose=0)
    if how == 'parens':
        return term.pretty_print(verbose=2)


def process_statement(trs, statement, verbosity, count, trace, path=None,
                      strategy='eager', output='one'):
    try:
        s = p.parser.parse(statement + ';')[0]
    except IndexError:
        return ''
    if s[0] == 'rule':
        p.add_rule(trs, s[1], s[2])
        return ''
    elif s[0] == 'term':
        term = p.make_term(s[1], signature=trs.signature.copy())
        evaled = term.rewrite(trs, max_steps=count, type=output, trace=trace,
                              strategy=strategy, states=['normal'])
        if output == 'all':
            for i, t in enumerate(set(evaled)):
                if verbosity >= 0:
                    print '{:d}: {}'.format(i, t.pretty_print(2*verbosity))
                else:
                    print '{:d}: {}'.format(i, t)
        else:
            if verbosity >= 0:
                if trace:
                    evaled = evaled.root
                    the_trace = []
                    while evaled.children != []:
                        evaled = evaled.children[0]
                        the_trace.append(evaled.term)
                    if the_trace == []:
                        the_trace.append(evaled.term)
                    return '\n'.join(t.pretty_print(2*verbosity)
                                     for t in the_trace)
                else:
                    return evaled.pretty_print(2*verbosity)
            else:
                if trace:
                    evaled = evaled.root
                    the_trace = []
                    while evaled.children != []:
                        evaled = evaled.children[0]
                        the_trace.append(evaled.term)
                    if the_trace == []:
                        the_trace.append(evaled.term)
                    return '\n'.join(str(t) for t in the_trace)
                else:
                    return str(evaled)
    elif s[0] == 'signature':
        p.add_signature(trs, s[1])
    elif s[0] == 'assumption':
        p.add_assumption(trs, s[1], path=path)
    else:
        return 'Oops! ' + str(s)


def main():
    arguments = docopt.docopt(__doc__, version="terf 0.0.1")
    output = arguments.get('--output', 'one')
    trace = (arguments.get('--trace', False) and output == 'one')
    path = arguments['--path'].split(':')
    path += [] if './' in path else ['./']
    strategy = arguments.get('--strategy', 'eager')
    if arguments['<filename>']:
        batch(arguments['<filename>'],
              int(arguments['--print']),
              int(arguments['--steps']),
              trace, path, strategy, output)
    else:
        repl(int(arguments['--print']),
             int(arguments['--steps']),
             trace, path, strategy, output)


if __name__ == "__main__":
    main()

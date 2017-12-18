import TeRF.Types.Application as App
import TeRF.Types.Variable as Var
import TeRF.Algorithms.Unify as u
import TeRF.Algorithms.Substitute as s
import numpy as np


def rewrite_head(term, trs, number):
    for rule in trs:
        sub = u.unify({(rule.lhs, term)}, kind='match')
        if sub is not None:
            options = rule.rhs
            if number == 'one':
                options = [np.random.choice(options)]
            return [s.substitute(o, sub) for o in options]


def rewrite_args(term, trs, number, strategy):
    for i, arg in enumerate(term.args):
        part = single_rewrite(arg, trs, number, strategy)
        if part is not None:
            return [App.App(
                term.head,
                term.args[:max(0, i)] + [p] + term.args[max(1, i+1):])
                    for p in part]
    return None


def rewrite_normal(term, trs, number):
    return (rewrite_head(term, trs, number) or
            rewrite_args(term, trs, number, strategy='normal'))


def rewrite_eager(term, trs, number):
    return (rewrite_args(term, trs, number, strategy='eager') or
            rewrite_head(term, trs, number))


def single_rewrite(term, trs, number='one', strategy='eager'):
    if isinstance(term, Var.Var):
        return None
    elif isinstance(term, App.App):
        if strategy in ['normal', 'lo', 'leftmost-outermost']:
            return rewrite_normal(term, trs, number)
        if strategy in ['eager', 'li', 'leftmost-innermost']:
            return rewrite_eager(term, trs, number)
    raise TypeError('not a term')

from LOTlib.Hypotheses.Proposers.Proposer import ProposalFailedException
from numpy.random import choice

from TeRF.Types import Rule


def choose_a_rule(xs):
    try:
        idx = choice(len(xs))
        rule = xs[idx]
        return rule, idx
    except ValueError:
        raise ProposalFailedException('choose_a_rule: ' +
                                      'TRS must have rules')


def make_a_rule(lhs, rhs):
    try:
        return Rule(lhs, rhs)
    except ValueError:
        raise ProposalFailedException('make_a_rule: bad rule')

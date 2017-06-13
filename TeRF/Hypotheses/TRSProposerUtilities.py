from LOTlib.Hypotheses.Proposers.Proposer import ProposalFailedException
from numpy.random import choice

from TeRF.TRS import TRSError, RR


def choose_a_rule(xs):
    try:
        idx = choice(len(xs))
        rule = xs[idx]
        return rule, idx
    except ValueError:
        raise ProposalFailedException('LocalDifferenceProposer: ' +
                                      'TRS must have rules')


def make_a_rule(lhs, rhs):
    try:
        return RR(lhs, rhs)
    except TRSError:
        raise ProposalFailedException('LocalDifferenceProposer: bad rule')

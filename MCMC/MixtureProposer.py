"""A mixture proposal (ONLY ERGODIC IF MIXTURE IS ERGODIC!)

Given a weighted list of other proposal methods, create a proposal which uses
these as subproposals in proportion to their weight.
"""

from LOTlib.Hypotheses.Proposers.TRS.Proposer import Proposer
from scipy.misc import logsumexp
from numpy.random import choice
from numpy import log


class MixtureProposer(Proposer):
    def __init__(proposers=[], weights=[], **kwargs):
        def propose_value(value, **kwargs):
            """sample a sub-proposer and propose from it"""
            proposer = choice(proposers, p=weights)
            return proposer(value, ret='value', **kwargs)

        def give_proposal_log_p(old, new, **kwargs):
            """prob. of generating new from old, adjusted for weight"""
            return logsumexp([p(old, newVal=new, ret='logp', **kwargs) + log(w)
                              for p, w in zip(proposers, weights)])

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

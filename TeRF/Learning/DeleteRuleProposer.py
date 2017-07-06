from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy.random import choice

from TeRF.Miscellaneous import find_insertion, log1of, log


def propose_value(old_value, **kwargs):
    try:
        chosen_rule = choice(old_value.rules)
        print 'drp: deleting', chosen_rule
        return deepcopy(old_value).del_rule(chosen_rule)
    except ValueError:
        raise ProposalFailedException('DeleteRuleProposer: TRS has no rules')


def give_proposal_log_p(old_value, new_value, **kwargs):
    if new_value.operators == old_value.operators and \
       find_insertion(old_value.rules, new_value.rules) is not None:
        return log1of(old_value.rules)
    return log(0)


class DeleteRuleProposer(Proposer):
    """
    Proposer for removing a rule from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S, R U {r}), where r is a rule, give a new TRS (S, R).
    """
    def __init__(self, **kwargs):
        """Create a DeleteRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DeleteRuleProposer, self).__init__(**kwargs)

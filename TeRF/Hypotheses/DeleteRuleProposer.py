from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice


def propose_value(old_value, **kwargs):
    if len(old_value.rules) == 0:
        raise ProposalFailedException('DeleteRuleProposer: ' +
                                      'No rules to Delete')
    else:
        # chosen_rule = choice(old_value.rules)
        # print 'proposing to delete', chosen_rule
        return deepcopy(old_value).del_rule(choice(old_value.rules))


def give_proposal_log_p(old_value, new_value, **kwargs):
    if len(old_value.rules) - len(new_value.rules) == 1 and \
       new_value.operators == old_value.operators and \
       new_value.variables == old_value.variables:
        rule = [r for r in old_value.rules if r not in new_value.rules][0]
        if hasattr(rule, 'lhs') and hasattr(rule, 'rhs'):
            return -log(len(old_value.rules))
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

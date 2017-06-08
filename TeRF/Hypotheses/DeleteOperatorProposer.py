from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice


def propose_value_maker(privileged_ops):
    def propose_value(old_value, **kwargs):
        try:
            privileged = privileged_ops if privileged_ops else set()
            chosen = choice(list(old_value.operators-privileged))
            return deepcopy(old_value).del_op(chosen)
        except ValueError:
            raise ProposalFailedException('DeleteOperatorProposer: ' +
                                          'No Operators to Delete')
    return propose_value


def give_proposal_log_p(old_value, new_value, **kwargs):
    difference = old_value.operators - new_value.operators
    if len(difference) == 1:
        operator = difference.pop()
        unchanged_rules = [r for r in old_value.rules
                           if operator not in r.operators()]
        if new_value.rules == unchanged_rules:
            return -log(len(old_value.operators))
    return log(0)


class DeleteOperatorProposer(Proposer):
    """
    Proposer for removing an operator from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S U {x}, R), where x is an operator, give a new TRS (S, R).
    """
    def __init__(self, privileged_ops=None, **kwargs):
            """Create a DeleteOperatorProposer"""
            self.propose_value = propose_value_maker(privileged_ops)
            self.give_proposal_log_p = give_proposal_log_p
            super(DeleteOperatorProposer, self).__init__(**kwargs)

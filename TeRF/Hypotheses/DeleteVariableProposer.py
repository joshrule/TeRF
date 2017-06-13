from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.Miscellaneous import log1of


def propose_value(old_value, **kwargs):
    try:
        chosen_var = choice(list(old_value.variables))
        # print 'dvp: deleting variable', chosen_var
        return deepcopy(old_value).del_var(chosen_var)
    except ValueError:
        raise ProposalFailedException('DeleteVariableProposer: ' +
                                      'No Variables to Delete')


def give_proposal_log_p(old_value, new_value, **kwargs):
    difference = old_value.variables - new_value.variables
    if len(difference) == 1:
        variable = difference.pop()
        unchanged_rules = [r for r in old_value.rules
                           if variable not in r.variables()]
        if new_value.rules == unchanged_rules:
            return log1of(old_value.variables)
    return log(0)


class DeleteVariableProposer(Proposer):
    """
    Proposer for removing a variable from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S U {x}, R), where x is a variable, give a new TRS (S, R).
    """
    def __init__(self, **kwargs):
        """Create a DeleteVariableProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DeleteVariableProposer, self).__init__(**kwargs)

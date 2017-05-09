from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from TRS import Var
from copy import copy
from numpy import log
from numpy.random import choice


class DeleteVariableProposer(Proposer):
    """
    Proposer for removing a variable from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S U {x}, R), where x is a variable, give a new TRS (S, R).
    """
    def __init__(gensym=None, **kwargs):
        """
        Create a DeleteVariableProposer
        """
        def propose_value(old_value, **kwargs):
            variables = [s for s in old_value.signature if isinstance(s, Var)]
            if len(variables) == 0:
                raise ProposalFailedException('DeleteVariableProposer: ' +
                                              'No Variables to Delete')
            else:
                new_value = copy(old_value).del_variable(choice(variables))
                return new_value

        def give_proposal_log_p(old_value, new_value, **kwargs):
            difference = old_value.signature - new_value.signature
            if len(difference) == 1:
                variable = difference.pop()
                unchanged_rules = [r for r in old_value.rules
                                   if variable not in r.variables]
                if isinstance(variable, Var) and \
                   new_value.rules == unchanged_rules:
                    variables = [s for s in old_value.signature
                                 if isinstance(s, Var)]
                    return -log(len(variables))
            return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

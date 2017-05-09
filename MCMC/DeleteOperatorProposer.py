from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from TRS import Op
from copy import copy
from numpy import log
from numpy.random import choice


class DeleteOperatorProposer(Proposer):
    """
    Proposer for removing an operator from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S U {x}, R), where x is an operator, give a new TRS (S, R).
    """
    def __init__(gensym=None, **kwargs):
        """
        Create a DeleteOperatorProposer
        """
        def propose_value(old_value, **kwargs):
            operators = [s for s in old_value.signature if isinstance(s, Op)]
            if len(operators) == 0:
                raise ProposalFailedException('DeleteOperatorProposer: ' +
                                              'No Operators to Delete')
            else:
                new_value = copy(old_value).del_operator(choice(operators))
                return new_value

        def give_proposal_log_p(old_value, new_value, **kwargs):
            difference = old_value.signature - new_value.signature
            if len(difference) == 1:
                operator = difference.pop()
                unchanged_rules = [r for r in old_value.rules
                                   if operator not in r.operators]
                if isinstance(operator, Op) and \
                   new_value.rules == unchanged_rules:
                    operators = [s for s in old_value.signature
                                 if isinstance(s, Op)]
                    return -log(len(operators))
            return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

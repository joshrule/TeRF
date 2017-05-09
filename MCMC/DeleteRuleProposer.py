from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from TRS import RewriteRule
from copy import copy
from numpy import log
from numpy.random import choice


class DeleteRuleProposer(Proposer):
    """
    Proposer for removing a rule from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S, R U {r}), where r is a rule, give a new TRS (S, R).
    """
    def __init__(gensym=None, **kwargs):
        """
        Create a DeleteRuleProposer
        """
        def propose_value(old_value, **kwargs):
            if len(old_value.rules) == 0:
                raise ProposalFailedException('DeleteRuleProposer: ' +
                                              'No rules to Delete')
            else:
                new_value = copy(old_value).del_rule(choice(old_value.rules))
                return new_value

        def give_proposal_log_p(old_value, new_value, **kwargs):
            difference = old_value.rules - new_value.rules
            if len(difference) == 1 and \
               new_value.signature == old_value.signature:
                rule = difference.pop
                if isinstance(rule, RewriteRule):
                    return -log(len(old_value.rules))
            return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

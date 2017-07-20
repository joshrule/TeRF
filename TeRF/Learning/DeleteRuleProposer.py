import copy
import LOTlib.Hypotheses.Proposers as P
import numpy.random as random
import TeRF.Miscellaneous as M


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    try:
        rule = random.choice(list(new_value.rules()))
    except ValueError:
        raise P.ProposalFailedException('DeleteRuleProposer: TRS has no rules')
    print 'drp: deleting', rule
    del new_value[rule]
    return new_value


def give_proposal_log_p(old, new, **kwargs):
    if new.signature == old.signature and old.find_insertion(new) is not None:
        return M.log1of(list(old.rules()))
    return M.log(0)


class DeleteRuleProposer(P.Proposer):
    """
    Proposer for removing a Rule from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S, R U {r}), where r is a Rule, give a new TRS (S, R).
    """
    def __init__(self, **kwargs):
        """Create a DeleteRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DeleteRuleProposer, self).__init__(**kwargs)

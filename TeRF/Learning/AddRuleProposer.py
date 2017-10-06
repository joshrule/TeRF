import copy
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as M


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    rule = new_value.signature.operators.sample_rule(p_rhs=1.0, invent=True)
    if rule in new_value:
        raise P.ProposalFailedException('rule already exists')
    print '# arp: adding rule', rule
    new_value.add(rule)
    return new_value


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature:
        rule = new.find_insertion(old)
        try:
            return -(1 + rule.size / 1.5)
            # return new.signature.operators.log_p_rule(rule, p_rhs=1.0,
            #                                           invent=True)
        except AttributeError:
            pass
    return M.log(0)


class AddRuleProposer(P.Proposer):
    """
    Proposer for adding a Rule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {r}), where r is a Rule.
    """
    def __init__(self, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(AddRuleProposer, self).__init__(**kwargs)

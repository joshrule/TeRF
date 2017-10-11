import copy
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as M
import TeRF.Learning.RationalRulesTRSGrammar as RR


def propose_value_maker(alpha):
    def propose_value(value, **kwargs):
        new_value = copy.deepcopy(value)
        g = RR.RationalRulesTRSGrammar(new_value.signature,
                                       alpha=alpha)
        counts = g.count_trs(new_value)
        g.counts = RR.merge_counts(g.counts, counts)
        rule = g.sample_rule()
        if rule in new_value:
            raise P.ProposalFailedException('rule already exists')
        print '# arp: adding rule', rule
        new_value.add(rule)
        return new_value
    return propose_value


def give_proposal_log_p_maker(alpha):
    def give_proposal_log_p(old, new, **kwargs):
        if old.signature == new.signature:
            rule = new.find_insertion(old)
            g = RR.RationalRulesTRSGrammar(new.signature,
                                           alpha=alpha)
            counts = g.count_trs(old)
            g.counts = RR.merge_counts(g.counts, counts)
            try:
                return g.log_p_rule(rule)
            except (TypeError, AttributeError):
                pass
        return M.log(0)
    return give_proposal_log_p


class AddRuleProposer(P.Proposer):
    """
    Proposer for adding a Rule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {r}), where r is a Rule.
    """
    def __init__(self, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value_maker(getattr(self, 'rrAlpha', 1.0))
        self.give_proposal_log_p = \
            give_proposal_log_p_maker(getattr(self, 'rrAlpha', 1.0))
        super(AddRuleProposer, self).__init__(**kwargs)

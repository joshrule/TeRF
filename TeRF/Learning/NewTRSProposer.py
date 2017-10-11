import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.RationalRulesTRSGrammar as RR


def propose_value_maker(alpha, p_rule):
    def propose_value(value, **kwargs):
        g = RR.RationalRulesTRSGrammar(value.signature.copy(),
                                       alpha=alpha)
        new_value = g.sample_trs(p_rule)
        print '# ntp: generating a new TRS'
        return new_value
    return propose_value


def give_proposal_log_p_maker(alpha, p_rule):
    def give_proposal_log_p(old, new, **kwargs):
        if old.signature == new.signature:
            g = RR.RationalRulesTRSGrammar(new.signature.copy(),
                                           alpha=alpha)
            return g.log_p_trs(new, p_rule)
        return -np.inf
    return give_proposal_log_p


class NewTRSProposer(P.Proposer):
    """
    Proposer for generating a new TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), return a TRS (S, R') with a new set of rules, R'.
    """
    def __init__(self, p_rules=0.5, **kwargs):
        """Create an AddRuleProposer"""
        alpha = getattr(self, 'rrAlpha', 1.0)
        self.propose_value = propose_value_maker(alpha, self.p_rules)
        self.give_proposal_log_p = give_proposal_log_p_maker(alpha,
                                                             self.p_rules)
        super(NewTRSProposer, self).__init__(**kwargs)

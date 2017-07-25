import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import scipy as sp
import TeRF.Types.TRS as TRS


def propose_value_maker(p_rules):
    def propose_value(value, **kwargs):
        new_value = TRS.TRS()
        new_value.signature = copy.deepcopy(value.signature)
        n_rules = sp.stats.geom.rvs(p=p_rules)
        while new_value.num_rules() < n_rules:
            rule = new_value.signature.sample_rule(p_rhs=1.0, invent=True)
            new_value.add(rule)
        print 'ntp: generating a new TRS'
        return new_value
    return propose_value


def give_proposal_log_p_maker(p_rules):
    def give_proposal_log_p(old, new, **kwargs):
        if old.signature == new.signature:
            n_rules = new.num_rules()+1
            p_the_rules = sum(new.signature.log_p_rule(rule, p_rhs=1.0,
                                                       invent=True)
                              for rule in new.rules())
            return sp.stats.geom.logpmf(k=n_rules, p=p_rules) + p_the_rules
        return -np.inf
    return give_proposal_log_p


class NewTRSProposer(P.Proposer):
    """
    Proposer for generating a new TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), return a TRS (S, R') with a new set of rules, R'.
    """
    def __init__(self, p_rules=0.5, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value_maker(self.p_rules)
        self.give_proposal_log_p = give_proposal_log_p_maker(self.p_rules)
        super(NewTRSProposer, self).__init__(**kwargs)

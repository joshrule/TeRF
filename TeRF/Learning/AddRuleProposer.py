from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)

from TeRF.Miscellaneous import find_insertion, log
from TeRF.Types import Rule, Sig


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    lhs = None
    while not hasattr(lhs, 'head'):
        lhs = Sig(value.operators).sample_term(invent=True)
    rhs = Sig(value.operators | lhs.variables()).sample_term(invent=False)
    try:
        new_rule = Rule(lhs, [rhs])
    except ValueError:
        raise ProposalFailedException('AddRuleProposer: bad rule')
    print 'arp: adding rule', new_rule
    return new_value.add_rule(new_rule)


def give_proposal_log_p(old, new, **kwargs):
    rule = find_insertion(new.rules, old.rules)
    if rule is not None and old.operators == new.operators:
        p_lhs = Sig(new.operators).log_p(rule.lhs, invent=True)
        rhs_sig = Sig(new.operators | rule.lhs.variables())
        p_rhs = rhs_sig.log_p(rule.rhs, invent=False)
        return (p_lhs + p_rhs)
    return log(0)


class AddRuleProposer(Proposer):
    """
    Proposer for adding a RewriteRule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {x}), where x is a rule, l -> r
    """
    def __init__(self, **kwargs):
        """Create a NewRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(AddRuleProposer, self).__init__(**kwargs)

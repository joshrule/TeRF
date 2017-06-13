from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Miscellaneous import find_insertion
from TeRF.Utilities import sample_term, log_p, alpha_eq


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    terminals = {x for x in value.operators if x.arity == 0} | value.variables
    if len(terminals) == 0:
        raise ProposalFailedException('AddRuleProposer: no terminals')
    try:
        curr_lhss = [r.lhs for r in value.rules]
        lhs = None
        blahs = [False]
        while (not hasattr(lhs, 'head')) or any(blahs):
            lhs = sample_term(value.variables | value.operators)
            protoblahs = [alpha_eq(lhs, clhs) for clhs in curr_lhss]
            blahs = [tf for tf, env in protoblahs]
        rhs = sample_term(value.operators | lhs.variables())
        new_rule = RewriteRule(lhs, rhs)
        idx = int(choice(len(value.rules)+1))
        # print 'arp: adding rule', new_rule
    except TRSError:
        raise ProposalFailedException('AddRuleProposer: ' +
                                      'couldn\'t generate new rule')
    return new_value.add_rule(new_rule, index=idx)


def give_proposal_log_p(old, new, **kwargs):
    rule = find_insertion(new.rules, old.rules)
    if rule is not None and \
       old.variables == new.variables and \
       old.operators == new.operators:
        p_lhs = log_p(rule.lhs, new.variables | new.operators)
        p_rhs = log_p(rule.rhs, new.operators | rule.lhs.variables())
        p_slot = -log(len(new.rules)) if new.rules != [] else log(1)
        return (p_lhs + p_rhs + p_slot)
    else:
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

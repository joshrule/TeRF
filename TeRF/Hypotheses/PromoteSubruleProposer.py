from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Miscellaneous import find_difference


def can_be_promoted(rule, promotion):
    return ((promotion == 'rhs' or len(rule.lhs.body) > 0) and
            (promotion == 'lhs' or (hasattr(rule.rhs, 'body') and
                                    len(rule.rhs.body) > 0)))


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    try:
        promotion = choice(['lhs', 'rhs', 'both'])
        rules = [r for r in new_value.rules if can_be_promoted(r, promotion)]
        rule = choice(rules)
    except ValueError:
        raise ProposalFailedException('PromoteSubruleProposer: ' +
                                      'TRS must have appropriate rules')
    try:
        new_lhs = (choice(rule.lhs.body) if promotion in ['lhs', 'both']
                   else rule.lhs)
        new_rhs = (choice(rule.rhs.body) if promotion in ['rhs', 'both']
                   else rule.rhs)
        new_rule = RewriteRule(new_lhs, new_rhs)
    except TRSError:  # can fail if the rule has lots of variables
        raise ProposalFailedException('PromoteSubruleProposer: ' +
                                      'bad rule')
    new_value.del_rule(rule)
    return new_value.add_rule(new_rule)


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            rules = old.rules
            p_method = -log(3)
            p_lhs = log(1)
            if old_rule.lhs != new_rule.lhs:
                p_lhs = -log(len(old_rule.lhs.body))
                rules = [r for r in rules if len(r.lhs.body) > 0]
            p_rhs = log(1)
            if old_rule.rhs != new_rule.rhs:
                p_rhs = -log(len(old_rule.rhs.body))
                rules = [r for r in rules
                         if hasattr(r.rhs, 'body') and len(r.rhs.body) > 0]
            p_choosing_rule = -log(len(rules))
            return p_method + p_choosing_rule + p_lhs + p_rhs
        except AttributeError:
            pass
    return log(0)


class PromoteSubruleProposer(Proposer):
    """
    Proposer for modifying a rule by promoting its children
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l' is an improper subtree of l, and r' of r.
    """
    def __init__(self, **kwargs):
        """Create a PromoteSubruleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(PromoteSubruleProposer, self).__init__(**kwargs)

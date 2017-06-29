from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import inf
from numpy.random import choice
from scipy.misc import logsumexp

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Miscellaneous import find_difference, log1of, log0


def can_be_promoted(rule, promotion):
    return ((promotion == 'rhs' or len(rule.lhs.body) > 0) and
            (promotion == 'lhs' or (hasattr(rule.rhs, 'body') and
                                    len(rule.rhs.body) > 0)))


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    try:
        promotion = choice(['lhs', 'rhs', 'both'])
        idxs = [i for i, r in enumerate(new_value.rules)
                if can_be_promoted(r, promotion)]
        idx = choice(idxs)
        rule = new_value.rules[idx]
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
    # print 'psp: changing', rule, 'to', new_rule
    new_value.rules[idx] = new_rule
    return new_value


def log_p_is_promotion(old, new):
    try:
        if old != new and new in old.body:
            return log1of(old.body)
    except AttributeError:
        pass
    return log0(0)


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            p_method = -log0(3)

            p_promote_lhs = log_p_is_promotion(old_rule.lhs, new_rule.lhs)
            p_promote_rhs = log_p_is_promotion(old_rule.rhs, new_rule.rhs)

            p_lhs = log0(0)
            if p_promote_rhs == -inf:
                rules = [r for r in old.rules if len(r.lhs.body) > 0]
                p_rule = log1of(rules)
                p_lhs = p_method + p_promote_lhs + p_rule

            p_rhs = log0(0)
            if p_promote_lhs == -inf:
                rules = [r for r in old.rules if hasattr(r.rhs, 'body') and
                         len(r.rhs.body) > 0]
                p_rule = log1of(rules)
                p_rhs = p_method + p_promote_rhs + p_rule

            rules = [r for r in old.rules if hasattr(r.rhs, 'body') and
                     len(r.rhs.body) > 0 and len(r.lhs.body) > 0]
            p_rule = log1of(rules)
            p_both = p_method + p_promote_lhs + p_promote_rhs + p_rule

            return logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return log0(0)


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

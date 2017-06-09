from copy import deepcopy
from itertools import permutations
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log, inf
from numpy.random import choice
from random import sample
from scipy.misc import logsumexp

from TeRF.TRS import App, RR, TRSError
from TeRF.Miscellaneous import find_difference


def can_be_swapped(rule, swap):
    return ((swap == 'rhs' or len(rule.lhs.body) > 1) and
            (swap == 'lhs' or (hasattr(rule.rhs, 'body') and
                               len(rule.rhs.body) > 1)))


def shuffle(xs):
    equal = True
    while equal:
        idxs = sample(xrange(len(xs)), len(xs))
        equal = (range(len(xs)) == idxs)
    return [xs[i] for i in idxs]


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    swap = choice(['lhs', 'rhs', 'both'])
    rules = [r for r in value.rules if can_be_swapped(r, swap)]
    try:
        rule = choice(rules)
    except ValueError:
        raise ProposalFailedException('PromoteSubruleProposer: ' +
                                      'TRS must have appropriate rules')
    try:
        new_lhs = App(rule.lhs.head, shuffle(rule.lhs.body)) \
                  if swap != 'rhs' else rule.lhs
        new_rhs = App(rule.rhs.head, shuffle(rule.rhs.body)) \
                  if swap != 'lhs' else rule.rhs
        new_rule = RR(new_lhs, new_rhs)
    except TRSError:
        raise ProposalFailedException('SwapSubruleProposer: bad rule')
    # print 'ssp: changing', rule, 'to', new_rule
    new_value.del_rule(rule)
    return new_value.add_rule(new_rule)


def log_p_is_a_swap(t1, t2):
    try:
        if t1.head == t2.head and len(t1.body) == len(t2.body) > 1:
            options = list(permutations(t1.body)).remove(tuple(t1.body))
            return log(options.count(tuple(t2.body))) - log(len(options))
    except AttributeError:
        pass
    return log(0)


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            p_method = -log(3)
            p_swap_lhs = log_p_is_a_swap(old_rule.lhs, new_rule.lhs)
            p_swap_rhs = log_p_is_a_swap(old_rule.rhs, new_rule.rhs)

            lhs_rules = [r for r in old.rules if len(r.lhs.body) > 1]
            p_lhs_rule = -log(len(lhs_rules)) if lhs_rules != [] else log(0)
            p_lhs = log(0)
            if p_swap_rhs == -inf:
                p_lhs = p_method + p_lhs_rule + p_swap_lhs

            rhs_rules = [r for r in old.rules
                         if hasattr(r.rhs, 'body') and len(r.rhs.body) > 1]
            p_rhs_rule = -log(len(rhs_rules)) if rhs_rules != [] else log(0)
            p_rhs = log(0)
            if p_swap_lhs == -inf:
                p_rhs = p_method + p_rhs_rule + p_swap_rhs

            both_rules = [r for r in old.rules if len(r.lhs.body) > 1 and
                          hasattr(r.rhs, 'body') and len(r.lhs.body) > 1]
            p_both_rule = -log(len(both_rules)) if both_rules != [] else log(0)
            p_both = p_method + p_both_rule + p_swap_lhs + p_swap_rhs

            return logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return log(0)


class SwapSubruleProposer(Proposer):
    """
    Proposer for modifying a rule by swapping the children of its trees
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l' has the same head and children as l, but
    the order of the children is permuted. The same is true for r' and r.
    """
    def __init__(self, **kwargs):
        """Create a SwapSubruleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(SwapSubruleProposer, self).__init__(**kwargs)

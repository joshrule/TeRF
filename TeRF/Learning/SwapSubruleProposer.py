import copy
import itertools as iter
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import scipy as sp
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A


def can_be_swapped(rule, swap):
    return (swap == 'rhs' or len(rule.lhs.body) > 1) and \
        (swap == 'lhs' or len(getattr(rule.rhs0, 'body', [])) > 1)


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    side = np.random.choice(['lhs', 'rhs', 'both'])
    rule = pu.choose_a_rule(new_value, lambda r: can_be_swapped(r, side))

    lhs = rule.lhs
    if side != 'rhs':
        try:
            lhs = A.App(rule.lhs.head, misc.unique_shuffle(rule.lhs.body))
        except TypeError:
            raise P.ProposalFailedException('SwapSubruleProposer: cannot swap')

    rhs = rule.rhs0
    if side != 'lhs':
        try:
            rhs = A.App(rule.rhs0.head, misc.unique_shuffle(rule.rhs0.body))
        except TypeError:
            raise P.ProposalFailedException('SwapSubruleProposer: cannot swap')

    new_rule = pu.make_a_rule(lhs, rhs)
    print 'ssp: changing', rule, 'to', new_rule
    return new_value.swap(rule, new_rule)


def log_p_is_a_swap(old, new):
    try:
        if old.head == new.head and len(old.body) == len(new.body) > 1:
            options = [x for x in iter.permutations(old.body)
                       if x != tuple(old.body)]
            return misc.logNof(options, n=options.count(tuple(new.body)))
    except (AttributeError, ValueError):
        pass
    return -np.inf


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature:
        old_rule, new_rule = old.find_difference(new)
        try:
            p_method = -misc.log(3)
            p_swap_lhs = log_p_is_a_swap(old_rule.lhs, new_rule.lhs)
            p_swap_rhs = sp.misc.logsumexp(
                [log_p_is_a_swap(rhs, new_rule.rhs0) for rhs in old_rule.rhs])

            p_lhs = -np.inf
            if p_swap_rhs == -np.inf:
                p_rule = misc.logNof([r for r in old.rules()
                                      if len(r.lhs.body) > 1])
                p_lhs = p_method + p_rule + p_swap_lhs

            p_rhs = -np.inf
            if p_swap_lhs == -np.inf:
                p_rhs_rule = misc.logNof(
                    [r for r in old.rules()
                     if len(getattr(r.rhs0, 'body', [])) > 1])
                p_rhs = p_method + p_rhs_rule + p_swap_rhs

            p_both_rule = misc.logNof(
                [r for r in old.rules() if len(r.lhs.body) > 1 and
                 len(getattr(r.rhs0, 'body', [])) > 1])
            p_both = p_method + p_both_rule + p_swap_lhs + p_swap_rhs

            return sp.misc.logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return -np.inf


class SwapSubruleProposer(P.Proposer):
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

import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import scipy as sp
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Miscellaneous as misc

choice = np.random.choice


def can_be_promoted(rule, promotion):
    return (promotion == 'rhs' or len(rule.lhs.body) > 0) and \
        (promotion == 'lhs' or len(getattr(rule.rhs, 'body', [])) > 0)


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    side = choice(['lhs', 'rhs', 'both'])
    rule = pu.choose_a_rule(new_value, lambda r: can_be_promoted(r, side))

    lhs = (choice(rule.lhs.body) if side in ['lhs', 'both'] else rule.lhs)
    rhs = (choice(rule.rhs0.body) if side in ['rhs', 'both'] else rule.rhs0)

    new_rule = pu.make_a_rule(lhs, rhs)
    print 'psp: changing', rule, 'to', new_rule
    return new_value.swap(rule, new_rule)


def log_p_is_promotion(old, new):
    try:
        return misc.logNof(old.body, n=old.body.count(new))
    except AttributeError:
        return -np.inf


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature:
        old_rule, new_rule = old.find_difference(new)
        try:
            p_method = -misc.log(3)

            p_promote_lhs = log_p_is_promotion(old_rule.lhs, new_rule.lhs)
            p_promote_rhs = log_p_is_promotion(old_rule.rhs0, new_rule.rhs0)

            p_lhs = -np.inf
            if p_promote_rhs == -np.inf:
                rules = [r for r in old.rules() if r.lhs.body]
                p_rule = misc.logNof(rules)
                p_lhs = p_method + p_promote_lhs + p_rule

            p_rhs = -np.inf
            if p_promote_lhs == -np.inf:
                rules = [r for r in old.rules() if getattr(r.rhs0, 'body', [])]
                p_rule = misc.logNof(rules)
                p_rhs = p_method + p_promote_rhs + p_rule

            rules = [r for r in old.rules()
                     if getattr(r.rhs0, 'body', []) and r.lhs.body]
            p_rule = misc.logNof(rules)
            p_both = p_method + p_promote_lhs + p_promote_rhs + p_rule

            return sp.misc.logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return -np.inf


class PromoteSubruleProposer(P.Proposer):
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

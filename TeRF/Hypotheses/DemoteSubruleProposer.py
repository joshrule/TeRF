from copy import copy, deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log, inf
from numpy.random import choice
from scipy.misc import logsumexp

from TeRF.TRS import RR, App, TRSError
from TeRF.Miscellaneous import find_difference
from TeRF.Utilities import sample_term, log_p


def demote(t, signature):
    operators = [o for o in signature
                 if hasattr(o, 'arity') and o.arity > 0]
    head = choice(operators)
    body = [sample_term(signature) for _ in xrange(head.arity-1)]
    idx = choice(head.arity)
    body.insert(idx, t)
    return App(head, body)


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    try:
        rule = choice(new_value.rules)
    except ValueError:
        raise ProposalFailedException('DemoteSubruleProposer: ' +
                                      'TRS must have rules')

    sides = choice(['lhs', 'rhs', 'both'])
    lhs_signature = value.operators | value.variables
    try:
        new_lhs = rule.lhs if sides == 'rhs' else demote(rule.lhs,
                                                         lhs_signature)
    except ValueError:
        raise ProposalFailedException('DemoteSubruleProposer: ' +
                                      'TRS must have suitable heads')

    rhs_signature = value.operators | new_lhs.variables()
    try:
        new_rhs = rule.rhs if sides == 'lhs' else demote(rule.rhs,
                                                         rhs_signature)
    except ValueError:
        raise ProposalFailedException('DemoteSubruleProposer: ' +
                                      'TRS must have suitable heads')

    try:
        new_rule = RR(new_lhs, new_rhs)
    except TRSError:
        raise ProposalFailedException('PromoteSubruleProposer: bad rule')

    # print 'dsp: changing', rule, 'to', new_rule
    new_value.del_rule(rule)
    return new_value.add_rule(new_rule)


def log_p_is_demotion(r1, r2, signature):
    if r1 != r2 and hasattr(r2, 'body') and r1 in r2.body:
        operators = [a for a in signature
                     if hasattr(a, 'arity') and a.arity > 0]
        p_op = -log(len(operators)) if r2.head in operators else log(0)

        branches = copy(r2.body)
        branches.remove(r1)
        p_branches = sum([log_p(b, signature) for b in branches])

        p_index = -log(len(r2.body))

        return p_op + p_branches + p_index
    return log(0)


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            p_method = -log(3)
            p_rule = -log(len(old.rules)) if old.rules != [] else log(0)
            p_demote_lhs = log_p_is_demotion(old_rule.lhs, new_rule.lhs,
                                             new.operators | new.variables)
            p_demote_rhs = log_p_is_demotion(old_rule.rhs, new_rule.rhs,
                                             new.operators |
                                             new_rule.lhs.variables())

            p_lhs = log(0)
            if p_demote_rhs == -inf:
                p_lhs = p_method + p_rule + p_demote_lhs

            p_rhs = log(0)
            if p_demote_lhs == -inf:
                p_rhs = p_method + p_rule + p_demote_rhs

            p_both = p_method + p_rule + p_demote_lhs + p_demote_rhs

            return logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return log(0)


class DemoteSubruleProposer(Proposer):
    """
    Proposer for modifying a rule by demoting it and adding a new head
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l is an immediate subtree of l', and r of r'.
    """
    def __init__(self, **kwargs):
        """Create a DemoteSubruleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DemoteSubruleProposer, self).__init__(**kwargs)

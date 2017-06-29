from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy.random import choice

from TeRF.Hypotheses.TRSProposerUtilities import choose_a_rule, make_a_rule
from TeRF.Miscellaneous import find_difference, log1of, log0
from TeRF.Utilities import differences


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    rule, idx = choose_a_rule(value.rules)
    diffs = differences(rule.lhs, rule.rhs)
    if (rule.lhs, rule.rhs) in diffs:
        diffs.remove((rule.lhs, rule.rhs))

    try:
        new_lhs, new_rhs = diffs[choice(len(diffs))]
    except ValueError:
        raise ProposalFailedException('LocalDifferenceProposer: ' +
                                      'no suitable differences')

    new_rule = make_a_rule(new_lhs, new_rhs)
    # print 'ldp: changing', rule, 'to', new_rule
    new_value.rules[idx] = new_rule
    return new_value


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            p_rule = log1of(old.rules)
            all_diffs = differences(old_rule.lhs, old_rule.rhs)
            if (old_rule.lhs, old_rule.rhs) in all_diffs:
                all_diffs.remove((old_rule.lhs, old_rule.rhs))
                p_diff = (log0(all_diffs.count((new_rule.lhs, new_rule.rhs))) +
                          log1of(all_diffs))
                return p_rule + p_diff
        except AttributeError:
            pass
    return log0(0)


class LocalDifferenceProposer(Proposer):
    """
    Proposer for modifying a rule by demoting it and adding a new head
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l' and r' are subtrees from l and r,
    respectively, such that l' and r' are different trees but occurred at the
    same position in l and r.
    """
    def __init__(self, **kwargs):
        """Create a LocalDifferenceProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(LocalDifferenceProposer, self).__init__(**kwargs)

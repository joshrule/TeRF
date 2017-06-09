from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RR, TRSError
from TeRF.Miscellaneous import find_difference
from TeRF.Utilities import local_differences


def propose_value(value, **kwargs):
    new_value = deepcopy(value)
    try:
        rule = choice(new_value.rules)
    except ValueError:
        raise ProposalFailedException('LocalDifferenceProposer: ' +
                                      'TRS must have rules')

    differences = local_differences(rule.lhs, rule.rhs)
    if differences == [] or differences == [(rule.lhs, rule.rhs)]:
        raise ProposalFailedException('LocalDifferenceProposer: ' +
                                      'no suitable differences')

    # print 'diffs:', differences
    new_lhs, new_rhs = differences[choice(len(differences))]
    try:
        new_rule = RR(new_lhs, new_rhs)
    except TRSError:
        raise ProposalFailedException('LocalDifferenceProposer: bad rule')

    print 'ldp: changing', rule, 'to', new_rule
    new_value.del_rule(rule)
    return new_value.add_rule(new_rule)


def give_proposal_log_p(old, new, **kwargs):
    if old.variables == new.variables and old.operators == new.operators:
        old_rule, new_rule = find_difference(old.rules, new.rules)
        try:
            p_choosing_rule = -log(len(old.rules))
            all_rules = local_differences(old_rule.lhs, old_rule.rhs)
            p_new_rule = (log(all_rules.count((new_rule.lhs, new_rule.rhs))) -
                          log(len(all_rules)))
            return p_choosing_rule + p_new_rule
        except AttributeError:
            pass
    return log(0)


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

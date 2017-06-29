from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy.random import choice
from scipy.stats import geom

from TeRF.Miscellaneous import log1of, log0
from TeRF.Utilities import sample_rules, log_p


# You can imagine making this proposal smarter by simply sampling new values
# for the holes created by the deleted variable, rather than sampling rules
# from whole cloth.

def propose_value_maker(p_rules):
    def propose_value(old_value, **kwargs):
        new_value = deepcopy(old_value)
        try:
            chosen_var = choice(list(new_value.variables))
        except ValueError:
            raise ProposalFailedException('DeleteVariableProposer: ' +
                                          'No Variables to Delete')
        print 'dvp: deleting variable', chosen_var
        new_value.del_var(chosen_var)
        if new_value.rules != old_value.rules:
            n_rules = geom.rvs(p=p_rules)-1
            rules = sample_rules(n_rules, None, new_value.operators,
                                 new_value.variables)
            for rule in rules:
                try:
                    idx = choice(len(new_value.rules))
                except ValueError:
                    idx = 0
                new_value.add_rule(rule, index=idx)
        return new_value
    return propose_value


def split_rules(var, new_rules, old_rules):
    unchanged = [r for r in new_rules + old_rules
                 if r in new_rules and r in old_rules]
    deleted = [r for r in new_rules + old_rules
               if r not in new_rules and r in old_rules]
    added = [r for r in new_rules + old_rules
             if r in new_rules and r not in old_rules]
    for rule in deleted:
        if var not in rule.variables():
            deleted = None
            break
    for rule in unchanged:
        if var in rule.variables():
            unchanged = None
            break
    for rule in added:
        if var in rule.variables():
            added = None
            break
    return deleted, unchanged, added


def give_proposal_log_p_maker(p_rules):
    def give_proposal_log_p(old_value, new_value, **kwargs):
        var_diff = old_value.variables - new_value.variables
        if len(var_diff) == 1:
            var = var_diff.pop()
            ds, us, ns = split_rules(var, new_value.rules, old_value.rules)
            if ds is not None or us is not None or ns is not None:
                p_var = log1of(old_value.variables)
                p_n_rules = geom.logpmf(k=len(ns)+1, p=p_rules)
                p_the_rules = log0(1)
                for rule in ns:
                    lhs_signature = new_value.variables | new_value.operators
                    p_lhs = log_p(rule.lhs, lhs_signature)
                    rhs_signature = rule.lhs.variables() | new_value.operators
                    p_rhs = log_p(rule.rhs, rhs_signature)
                    p_the_rules += (p_lhs + p_rhs)
                return p_var + p_n_rules + p_the_rules
        return log0(0)
    return give_proposal_log_p


class DeleteVariableProposer(Proposer):
    """
        Proposer for removing a variable from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S U {x}, R), where x is a variable, give a new TRS (S, R).
        """
    def __init__(self, p_rules=0.0, **kwargs):
        """Create a DeleteVariableProposer"""
        self.propose_value = propose_value_maker(p_rules)
        self.give_proposal_log_p = give_proposal_log_p_maker(p_rules)
        super(DeleteVariableProposer, self).__init__(**kwargs)

from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import Proposer
from numpy.random import choice
from scipy.stats import bernoulli

from TeRF.Miscellaneous import find_insertion, log0
from TeRF.TRS import Var
from TeRF.Utilities import log_p, sample_rules, unify


def rule_match(oldr, newr):
    succ1, env = unify(newr.lhs, oldr.lhs, type='match')
    succ2, _ = unify(newr.rhs, oldr.rhs, env=env, type='match')
    return succ1 and succ2


def propose_value_maker(gensym, p_rules):
    def propose_value(old_value, **kwargs):
        var = Var(name=gensym())
        new_value = deepcopy(old_value).add_var(var)
        n_rules = bernoulli.rvs(p=p_rules)
        rules = sample_rules(n_rules, var, new_value.operators,
                             new_value.variables)
        del_rules = []
        fst_del = None
        for newr in rules:
            for i, oldr in enumerate(new_value.rules):
                if rule_match(oldr, newr):
                    new_value.del_rule(oldr)
                    del_rules.append(oldr)
                    if fst_del is None:
                        fst_del = i
        if rules != []:
            if fst_del is None:
                if len(new_value.rules) > 0:
                    idx = choice(len(new_value.rules))
                else:
                    idx = 0
            else:
                idx = fst_del
            new_value.add_rule(rules[0], index=idx)
        print 'avrp: adding variable', var, ' and rule(s)', rules, \
            'while deleting', del_rules
        return new_value
    return propose_value


def find_variable_rule(new_var, new_rules, old_rules):
    rule_diff = set(new_rules) - set(old_rules)
    if len(rule_diff) == 1:
        new_rule = rule_diff.pop()
        if new_var in new_rule.variables():
            matches = filter(lambda r: rule_match(r, new_rule),
                             old_rules)
            non_matches = filter(lambda r: not rule_match(r, new_rule),
                                 old_rules)
            candidate = find_insertion(new_rules, non_matches)
            if candidate is not None:
                return candidate, matches
    return None, None


def give_proposal_log_p_maker(p_rules):
    def give_proposal_log_p(old_value, new_value, **kwargs):
        var_difference = new_value.variables - old_value.variables
        if len(var_difference) == 1:
            new_var = var_difference.pop()
            new_rule, matches = find_variable_rule(new_var, new_value.rules,
                                                   old_value.rules)
            if new_rule is not None and \
               old_value.operators == new_value.operators:
                lhs_signature = new_value.operators | new_value.variables
                p_lhs = log_p(new_rule.lhs, lhs_signature)
                rhs_signature = new_value.operators | new_rule.lhs.variables()
                p_rhs = log_p(new_rule.rhs, rhs_signature)
                p_slot = log0(1)
                if len(new_value.rules) > 1 and len(matches) == 0:
                    p_slot = -log0(len(new_value.rules)-1)
                p_rule = p_lhs + p_rhs + p_slot
                return p_rule + bernoulli.logpmf(k=1, p=p_rules)
            if old_value.operators == new_value.operators:
                return bernoulli.logpmf(k=0, p=p_rules)
        return log0(0)
    return give_proposal_log_p


class AddVariableRuleProposer(Proposer):
    """
    Proposer for adding a variable to a TRS, along with a rule using it
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {x}, R U {r}), where x is a new
    variable, and r is a new rule using x on the lhs. Names are gensyms.
    """
    def __init__(self, gensym=None, p_atom_rules=0.0, **kwargs):
        """
        Create an AddVariableProposer

        Args:
          gensym: a function which generates unique strings.
        """
        self.propose_value = propose_value_maker(gensym, p_atom_rules)
        self.give_proposal_log_p = give_proposal_log_p_maker(p_atom_rules)
        super(AddVariableRuleProposer, self).__init__(**kwargs)

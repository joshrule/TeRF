from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import Proposer
from numpy.random import choice
from scipy.stats import geom

from TeRF.Miscellaneous import log0
from TeRF.TRS import Var
from TeRF.Utilities import log_p, sample_rules


def propose_value_maker(gensym, p_rules):
    def propose_value(old_value, **kwargs):
        var = Var(name=gensym())
        new_value = deepcopy(old_value).add_var(var)
        n_rules = geom.rvs(p=p_rules)-1
        rules = sample_rules(n_rules, var, new_value.operators,
                             new_value.variables)
        for rule in rules:
            idx = choice(len(new_value.rules)+1)
            new_value.add_rule(rule, index=idx)
        # print 'avrp: adding variable', var, 'and rules', rules
        return new_value
    return propose_value


def give_proposal_log_p_maker(p_rules):
    def give_proposal_log_p(old_value, new_value, **kwargs):
        var_difference = new_value.variables - old_value.variables
        rule_difference = set(new_value.rules)-set(old_value.rules)
        if len(var_difference) == 1 and \
           old_value.operators == new_value.operators:
            p_the_rules = 0
            for i, rule in enumerate(rule_difference):
                lhs_signature = new_value.operators | new_value.variables
                p_lhs = log_p(rule.lhs, lhs_signature)
                rhs_signature = new_value.operators | rule.lhs.variables()
                p_rhs = log_p(rule.rhs, rhs_signature)
                p_slot = -log0(len(old_value.rules)+i) \
                    if len(old_value.rules)+i > 0 else log0(0)
                p_the_rules += (p_lhs + p_rhs + p_slot)
            return p_the_rules + geom.logpmf(k=len(rule_difference)+1,
                                             p=p_rules)
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

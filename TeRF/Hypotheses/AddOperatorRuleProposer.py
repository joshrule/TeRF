from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import Proposer
from numpy import log
from numpy.random import choice
from scipy.stats import geom

from TeRF.TRS import Op
from TeRF.Utilities import log_p, sample_rules


def propose_value_maker(gensym, p_arity, p_rules):
    def propose_value(old_value, **kwargs):
        op = Op(name=gensym(), arity=geom.rvs(p=p_arity)-1)
        new_value = deepcopy(old_value).add_op(op)
        n_rules = geom.rvs(p=p_rules)-1
        rules = sample_rules(n_rules, op, new_value.operators,
                             new_value.variables)
        for rule in rules:
            idx = choice(len(new_value.rules)+1)
            new_value.add_rule(rule, index=idx)
        # print 'aorp: adding operator', op, 'and rules', rules
        return new_value
    return propose_value


def give_proposal_log_p_maker(p_arity, p_rules):
    def give_proposal_log_p(old_value, new_value, **kwargs):
        op_difference = new_value.operators - old_value.operators
        rule_difference = set(new_value.rules)-set(old_value.rules)
        if len(op_difference) == 1 and \
           old_value.variables == new_value.variables:
            op = op_difference.pop()
            p_op = geom.logpmf(k=op.arity+1, p=p_arity)
            p_the_rules = 0
            for i, rule in enumerate(rule_difference):
                lhs_signature = new_value.operators | new_value.variables
                p_lhs = log_p(rule.lhs, lhs_signature)
                rhs_signature = new_value.operators | rule.lhs.variables()
                p_rhs = log_p(rule.rhs, rhs_signature)
                p_slot = -log(len(old_value.rules)+i)
                p_the_rules += (p_lhs + p_rhs + p_slot)
            return p_op + p_the_rules + geom.logpmf(k=len(rule_difference)+1,
                                                    p=p_rules)
        else:
            return log(0)
    return give_proposal_log_p


class AddOperatorRuleProposer(Proposer):
    """
    Proposer for adding an Operator to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {s}, R), where s is a new Operator.
    Names are gensyms, and arities are geometrically distributed.
    """
    def __init__(self, p_arity=None, gensym=None, p_atom_rules=0.0, **kwargs):
        """
        Create an AddOperatorProposer

        Args:
          p_arity: a float, 0 < x < 1, the rate for the geometric distribution
              from which arities are sampled.
          gensym: a function which generates unique strings.
        """

        if 0 > p_arity or p_arity > 1:
            raise ValueError('AddOperatorRuleProposer: p is out of bounds')

        self.propose_value = propose_value_maker(gensym, p_arity, p_atom_rules)
        self.give_proposal_log_p = give_proposal_log_p_maker(p_arity,
                                                             p_atom_rules)
        super(AddOperatorRuleProposer, self).__init__(**kwargs)

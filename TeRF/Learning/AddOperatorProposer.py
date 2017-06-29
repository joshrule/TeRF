from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import Proposer
from numpy import log
from scipy.stats import geom

from TeRF.TRS import Op


def propose_value_maker(gensym, p_arity):
    def propose_value(old_value, **kwargs):
        op = Op(name=gensym(),
                arity=geom.rvs(p=p_arity)-1)
        return deepcopy(old_value).add_op(op)
    return propose_value


def give_proposal_log_p_maker(p_arity):
    def give_proposal_log_p(old_value, new_value, **kwargs):
        difference = new_value.operators - old_value.operators
        if len(difference) == 1 and \
           old_value.variables == new_value.variables and \
           old_value.rules == new_value.rules:
            return geom.logpmf(k=difference.pop().arity+1, p=p_arity)
        return log(0)
    return give_proposal_log_p


class AddOperatorProposer(Proposer):
    """
    Proposer for adding an Operator to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {s}, R), where s is a new Operator.
    Names are gensyms, and arities are geometrically distributed.
    """
    def __init__(self, p_arity=None, gensym=None, **kwargs):
        """
        Create an AddOperatorProposer

        Args:
          p_arity: a float, 0 < x < 1, the rate for the geometric distribution
              from which arities are sampled.
          gensym: a function which generates unique strings.
        """

        if 0 > p_arity or p_arity > 1:
            raise ValueError('AddOperatorProposer: p is out of bounds')

        self.propose_value = propose_value_maker(gensym, p_arity)
        self.give_proposal_log_p = give_proposal_log_p_maker(p_arity)
        super(AddOperatorProposer, self).__init__(**kwargs)

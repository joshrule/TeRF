from LOTlib.Hypotheses.Proposers.TRS.Proposer import Proposer
from TRS import Operator
from copy import copy
from numpy import log
from scipy.stats import geom


class AddOperatorProposer(Proposer):
    """
    Proposer for adding an Operator to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {s}, R), where s is a new Operator.
    Names are gensyms, and arities are geometrically distributed.
    """
    def __init__(p_arity=None, gensym=None, **kwargs):
        """
        Create an AddOperatorProposer

        Args:
          p_arity: a float, 0 < x < 1, the rate for the geometric distribution
              from which arities are sampled.
          gensym: a function which generates unique strings.
        """
        def propose_value(old_value, **kwargs):
            operator = Operator(name=gensym(), arity=geom.rvs(p=p_arity))
            new_value = copy(old_value)
            return new_value.add_operator(operator)

        def give_proposal_log_p(old_value, new_value, **kwargs):
            difference = new_value.signature - old_value.signature
            if len(difference) == 1 and old_value.rules == new_value.rules:
                operator = difference.pop()
                if isinstance(operator, Operator):
                    return geom.logpmf(k=operator.arity, p=p_arity)
            return log(0)

        if 0 > p_arity or p_arity > 1:
            raise ValueError('AddOperatorProposer: p is out of bounds')
        
        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

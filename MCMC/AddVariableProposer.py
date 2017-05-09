from LOTlib.Hypotheses.Proposers.TRS.Proposer import Proposer
from TRS import Variable
from copy import copy
from numpy import log


class AddVariableProposer(Proposer):
    """
    Proposer for adding a variable to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {x}, R), where x is a new variable.
    Names are gensyms.
    """
    def __init__(gensym=None, **kwargs):
        """
        Create an AddVariableProposer

        Args:
          gensym: a function which generates unique strings.
        """
        def propose_value(old_value, **kwargs):
            variable = Variable(name=gensym())
            new_value = copy(old_value)
            return new_value.add_variable(variable)

        def give_proposal_log_p(old_value, new_value, **kwargs):
            difference = new_value.signature - old_value.signature
            if len(difference) == 1 and old_value.rules == new_value.rules:
                variable = difference.pop()
                if isinstance(variable, Variable):
                    return log(1)
            return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import Proposer
from numpy import log

from TeRF.TRS import Variable


def propose_value_maker(gensym):
    def propose_value(old_value, **kwargs):
        return deepcopy(old_value).add_var(Variable(name=gensym()))
    return propose_value


def give_proposal_log_p(old_value, new_value, **kwargs):
    difference = new_value.variables - old_value.variables
    if len(difference) == 1 and \
       old_value.operators == new_value.operators and \
       old_value.rules == new_value.rules:
        return log(1)
    return log(0)


class AddVariableProposer(Proposer):
    """
    Proposer for adding a variable to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S U {x}, R), where x is a new variable.
    Names are gensyms.
    """
    def __init__(self, gensym=None, **kwargs):
        """
        Create an AddVariableProposer

        Args:
          gensym: a function which generates unique strings.
        """
        self.propose_value = propose_value_maker(gensym)
        self.give_proposal_log_p = give_proposal_log_p
        super(AddVariableProposer, self).__init__(**kwargs)

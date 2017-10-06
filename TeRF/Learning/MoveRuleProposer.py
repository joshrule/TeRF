import copy
import numpy as np
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as misc


def propose_value(value, **kwargs):
    if len(value) < 2:
        raise P.ProposalFailedException('MoveRule: too few rules')
    new_value = copy.deepcopy(value)
    old_idx = np.random.choice(len(value))
    new_idx = np.random.choice(len(value)-1)
    print '# mrp: moving rule', old_idx, 'to', new_idx
    new_value.move(old_idx, new_idx)
    return new_value


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature and \
       old.find_move(new) != (None, None):
        return misc.logNof([1]*len(old)) + misc.logNof([1]*(len(old)-1))
    return misc.log(0)


class MoveRuleProposer(P.Proposer):
    """
    Proposer for moving a Rule in a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R), where R is reordered.
    """
    def __init__(self, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(MoveRuleProposer, self).__init__(**kwargs)

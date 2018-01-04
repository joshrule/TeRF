import numpy as np
import LOTlib.Hypotheses.Proposers as P
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Miscellaneous as misc


@utils.propose_value_template
def propose_value(value, **kwargs):
    if len(value.semantics) < 2:
        raise P.ProposalFailedException('MoveRule: too few rules')
    old_idx = np.random.choice(len(value.semantics))
    new_idx = np.random.choice([idx for idx in xrange(len(value.semantics))
                                if idx != old_idx])
    value.semantics.move(old_idx, new_idx)


@utils.validate_syntax
def give_proposal_log_p(old, new, **kwargs):
    # TODO: fix the underestimation that occurs when moves are adjacent
    if utils.there_was_a_move(old.semantics, new.semantics):
        return misc.logNof([1]*len(old.semantics)) + \
            misc.logNof([1]*(len(old.semantics)-1))
    return -np.inf


class MoveRuleProposer(P.Proposer):
    """
    Proposer for moving a Rule in a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R), where R is reordered.
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(MoveRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_p)

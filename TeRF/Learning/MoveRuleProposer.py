import itertools as itools
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

# TODO: underestimates probability when moves are adjacent
@utils.validate_syntax
def give_proposal_log_fb(old, new, **kwargs):
    old_clauses = old.semantics.clauses
    new_clauses = new.semantics.clauses
    old_set = set(old_clauses)
    new_set = set(new_clauses)

    if old_set == new_set and \
       not all(o.lhs == n.lhs
               for o, n in itools.izip(old_clauses, new_clauses)):
        f_or_b = misc.logNof([1]*len(old.semantics)) + \
                 misc.logNof([1]*(len(old.semantics)-1))
        return (f_or_b, f_or_b)
    return (-np.inf, -np.inf)



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

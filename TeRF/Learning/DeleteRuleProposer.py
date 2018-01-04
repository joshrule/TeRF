import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Miscellaneous as misc


@utils.propose_value_template
def propose_value(value, **kwargs):
    try:
        del value.semantics[np.random.choice(list(value.semantics.clauses))]
    except ValueError:
        raise P.ProposalFailedException('DeleteRule: Grammar has no rules')


@utils.validate_syntax
def give_proposal_log_p(old, new, **kwargs):
    if utils.find_insertion(old.semantics, new.semantics) is not None:
        return misc.logNof(list(old.semantics.clauses))
    return -np.inf


class DeleteRuleProposer(P.Proposer):
    """
    Proposer for removing a Rule from a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S, R U {r}), where r is a Rule, give a new TRS (S, R).
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DeleteRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_p)

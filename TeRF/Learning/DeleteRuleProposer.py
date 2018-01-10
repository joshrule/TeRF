import itertools as itools
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils


@utils.propose_value_template
def propose_value(value, **kwargs):
    try:
        del value.semantics[np.random.choice(value.semantics.clauses)]
    except ValueError:
        raise P.ProposalFailedException('DeleteRule: Grammar has no rules')

@utils.validate_syntax
def give_proposal_log_fb(old, new, **kwargs):
    old_clauses = old.semantics.clauses
    new_clauses = new.semantics.clauses
    old_set = set(old_clauses)
    new_set = set(new_clauses)
    diff = old_set.symmetric_difference(new_set)

    if len(diff) == 1:
        clause = diff.pop()
        try:  # forward delete
            old_clauses.remove(clause)
            if all(o.lhs == n.lhs
                   for o, n in itools.izip(old_clauses, new_clauses)):
                return (-np.log(len(new_clauses)+1), -np.inf)
        except ValueError:  # backward delete
            new_clauses.remove(clause)
            if all(o.lhs == n.lhs
                   for o, n in itools.izip(old_clauses, new_clauses)):
                return (-np.inf, -np.log(len(new_clauses)+1))
    return (-np.inf, -np.inf)


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

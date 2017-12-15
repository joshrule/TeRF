import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.Sampling as s


@utils.propose_value_template
def propose_value(value, **kwargs):
    rule = s.sample_rule(value.semantics.rule_type, value.syntax, invent=True)
    if rule in value.semantics:
        raise P.ProposalFailedException('AddRule: rule already exists')
    value.semantics.add(rule)


@utils.validate_syntax
def give_proposal_log_p(old, new, **kwargs):
    rule = utils.find_insertion(new.semantics, old.semantics)
    try:
        return s.log_p_rule(rule, old.semantics.rule_type, old.syntax,
                            invent=True)
    except AttributeError:
        return -np.inf


class AddRuleProposer(P.Proposer):
    """
    Proposer for adding a Rule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {r}), where r is a Rule.
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(AddRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_p)

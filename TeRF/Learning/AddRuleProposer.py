import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.Sampling as s
import TeRF.Miscellaneous as misc


@utils.propose_value_template
def propose_value_maker(templates):
    def propose_value(value, **kwargs):
        template = np.random.choice(templates)
        rule = s.fill_template(template, value.syntax, invent=True)
        if rule in value.semantics:
            raise P.ProposalFailedException('AddRule: rule already exists')
        value.semantics.add(rule)
    return propose_value


@utils.validate_syntax
def give_proposal_log_p_maker(templates):
    def give_proposal_log_p(old, new, **kwargs):
        rule = utils.find_insertion(new.semantics, old.semantics)
        try:
            return misc.logsumexp([s.lp_template(rule, t,
                                                 old.syntax, invent=True)
                                   for t in templates])
        except AttributeError:
            return -np.inf
    return give_proposal_log_p


class AddRuleProposer(P.Proposer):
    """
    Proposer for adding a Rule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {r}), where r is a Rule.
    """
    def __init__(self, templates=None, **kwargs):
        self.propose_value = propose_value_maker(templates)
        self.give_proposal_log_p = give_proposal_log_p_maker(templates)
        super(AddRuleProposer, self).__init__(**kwargs)


# if __name__ == "__main__":
#     utils.test_a_proposer(propose_value, give_proposal_log_p)

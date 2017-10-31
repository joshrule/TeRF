import LOTlib.Hypotheses.Proposers as P
import numpy.random as random
from scipy import misc as smisc
import TeRF.Learning.ProposerUtilities as utils


@utils.propose_value_template
def propose_value(value, **kwargs):
    start = random.choice([rule.lhs for rule in value.syntax])
    print 'starting at', start.to_string()
    rule = value.syntax.sample_rule(start=start)
    if rule in value.semantics:
        raise P.ProposalFailedException('AddRule: rule already exists')
    value.semantics.add(rule)


@utils.validate_syntax_and_primitives
def give_proposal_log_p(old, new, **kwargs):
    rule = utils.find_insertion(new.semantics, old.semantics)
    try:
        ps = [rule.log_p(old.syntax, start=r.lhs) for r in old.syntax]
        return smisc.logsumexp(ps)
    except AttributeError:
        pass


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

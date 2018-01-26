import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.TRSUtils as trsu
import TeRF.Algorithms.Sampling as s


def propose_value_maker(templates):
    @utils.propose_value_template
    def propose_value(value, **kwargs):
        template = np.random.choice(templates)
        sub = trsu.typecheck_full(value.semantics, value.syntax, {})
        # print 'trsu sub'
        # for k, v in sub.items():
        #     print '   ', k, ':', v
        # print 'trsu env'
        # for k, v in value.syntax.items():
        #     print '   ', k, ':', v
        rule = s.fill_template(template, value.syntax, sub, invent=True)
        if rule in value.semantics:
            raise P.ProposalFailedException('AddRule: rule already exists')
        value.semantics.add(rule)
        # print '# proposing:', rule
    return propose_value


def give_proposal_log_fb_maker(templates):
    @utils.validate_syntax
    def give_proposal_log_fb(old, new, **kwargs):
        old_clauses = old.semantics.clauses
        new_clauses = new.semantics.clauses
        old_set = set(old_clauses)
        new_set = set(new_clauses)
        on_diff = old_set - new_set
        if len(on_diff) == 1:
            return (-np.inf, 0.0)
        no_diff = new_set - old_set
        if len(no_diff) == 1:
            return (0.0, -np.inf)
        return (-np.inf, -np.inf)
    return give_proposal_log_fb


class AddRuleProposer(P.Proposer):
    """
    Proposer for adding a Rule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {r}), where r is a Rule.
    """
    def __init__(self, templates=None, **kwargs):
        self.propose_value = propose_value_maker(templates)
        self.give_proposal_log_fb = give_proposal_log_fb_maker(templates)
        super(AddRuleProposer, self).__init__(**kwargs)


# if __name__ == "__main__":
#     utils.test_a_proposer(propose_value, give_proposal_log_p)

import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.Sampling as s
import TeRF.Miscellaneous as misc


def propose_value_maker(templates):
    @utils.propose_value_template
    def propose_value(value, **kwargs):
        template = np.random.choice(templates)
        rule = s.fill_template(template, value.syntax, {}, invent=True)
        if rule in value.semantics:
            raise P.ProposalFailedException('AddRule: rule already exists')
        value.semantics.add(rule)
        print 'proposing:', rule
    return propose_value


def give_proposal_log_fb_maker(templates):
    @utils.validate_syntax
    def give_proposal_log_fb(old, new, **kwargs):
        old_clauses = old.semantics.clauses
        new_clauses = new.semantics.clauses
        len_difference = len(old_clauses) - len(new_clauses)
        # print 'len_difference', len_difference
        if len_difference == 1:  # old bigger than new
            old_set = set(old_clauses)
            new_set = set(new_clauses)
            diff = old_set - new_set
            # print 'len(diff)', len(diff)
            if len(diff) == 1:
                clause = diff.pop()
                b = misc.logsumexp([
                    misc.logNof(templates) +
                    s.lp_template(clause, t, old.syntax, {}, invent=True)
                    for t in templates])
                return (-np.inf, b)
        elif len_difference == -1:
            old_set = set(old_clauses)
            new_set = set(new_clauses)
            diff = new_set - old_set
            if len(diff) == 1:
                clause = diff.pop()
                f = misc.logsumexp([
                    misc.logNof(templates) +
                    s.lp_template(clause, t, old.syntax, {}, invent=True)
                    for t in templates])
                return (f, -np.inf)
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

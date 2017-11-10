import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Miscellaneous as misc
import TeRF.Types.Grammar as Grammar
import TeRF.Types.Parse as Parse


@utils.propose_value_template
def propose_value(value, **kwargs):
    rule = utils.choose_a_rule(value.semantics)

    triples = list(Parse.RuleParse(value.syntax, rule, start=None)
                   .find_resample_points())

    new_rule = copy.deepcopy(rule)
    tries = 0
    while new_rule.unify(rule, type='alpha') is not None and tries < 5:
        tries += 1
        try:
            t = triples[np.random.choice(len(triples))]
        except ValueError:
            raise P.ProposalFailedException('RegenerateRule: proposal failed')

        try:
            resampling_rhs = (t[0][0] == 'rhs')
        except:
            print 'triples', triples
            print 't', t
            print 't[0]', t[0]
            raise ValueError
        with Grammar.scope(value.syntax, scope=t[2], lock=resampling_rhs):
            new_term = value.syntax.sample_term(start=t[1])
        try:
            new_rule = copy.deepcopy(rule).replace(t[0], new_term)
        except ValueError as e:
            print e
            pass

    value.semantics.replace(rule, new_rule)


def p_resample(grammar, new, old, triple):
    with Grammar.scope(grammar, scope=triple[2]):
        try:
            old_subterm = old.place(triple[0])
            new_subterm = new.place(triple[0])
        except ValueError:
            p_resample = -np.inf
        else:
            if old_subterm != new_subterm:
                p_resample = new_subterm.log_p(grammar, start=triple[1])
            else:
                p_resample = -np.inf
    return p_resample


@utils.validate_syntax_and_primitives
def give_proposal_log_p(old, new, **kwargs):
    new_rule, old_rule = utils.find_difference(new.semantics, old.semantics)
    try:
        p_rule = misc.logNof(list(old.semantics.clauses))

        triples = (Parse.RuleParse(old.syntax, old_rule, start=None)
                   .find_resample_points())

        p_t = misc.logNof(triples)

        p_resamples = [(p_t + p_resample(old.syntax, new_rule, old_rule, t))
                       for t in triples]

        return p_rule + misc.logsumexp(p_resamples)
    except AttributeError as e:
        print e
        pass


class RegenerateRuleProposer(P.Proposer):
    """
    Proposer for regenerating a rule (NON-ERGODIC)

    For a Grammar R U {x}, give R U {x'}, where x is a rule, l -> r, x' is
    l' -> r', and either l != l' OR r != r', but not both.
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(RegenerateRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_p)

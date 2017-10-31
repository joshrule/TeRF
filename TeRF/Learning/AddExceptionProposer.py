import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Miscellaneous as misc
import TeRF.Learning.ProposerUtilities as utils


def propose_value_maker(data):
    @utils.propose_value_template
    def propose_value(value, **kwargs):
        try:
            ok_data = [datum for datum in data if datum not in value.semantics]
            ps = misc.renormalize([1./float(datum.size) for datum in ok_data])
            rule = copy.deepcopy(np.random.choice(ok_data, p=ps))
        except (TypeError, ValueError):
            raise P.ProposalFailedException('AddException: no new exceptions')
        value.semantics.add(rule)
    return propose_value


def give_proposal_log_p_maker(data):
    @utils.validate_syntax_and_primitives
    def give_proposal_log_p(old, new, **kwargs):
        rule = utils.find_insertion(new.semantics, old.semantics)
        try:
            ok_data = [(d, d.unify(rule, type='alpha') is not None)
                       for d in data if d not in old.semantics]
            ps = misc.renormalize([1./float(d[0].size) for d in ok_data])
            return misc.log(sum(p for p, d in zip(ps, ok_data) if d[1]))
        except (ValueError, TypeError, AttributeError):
            pass
    return give_proposal_log_p


class AddExceptionProposer(P.Proposer):
    """
    Proposer for adding an exception to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {e}), where e is a Rule taken
    verbatim from the initial data.
    """
    def __init__(self, data=None, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value_maker(data)
        self.give_proposal_log_p = give_proposal_log_p_maker(data)
        super(AddExceptionProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    import TeRF.Test.test_grammars as tg
    data = [tg.head_datum_T,
            tg.head_datum_T2,
            tg.head_datum_T3]
    
    utils.test_a_proposer(propose_value_maker(data),
                          give_proposal_log_p_maker(data))

import copy
import itertools as itools
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
    @utils.validate_syntax
    def give_proposal_log_p(old, new, **kwargs):
        old_clauses = old.semantics.clauses
        old_set = set(old_clauses)
        new_set = set(new.semantics.clauses)
        diff = new_set - old_set

        if len(diff) == 1:
            clause = diff.pop()
            ok = [d for d in data if d not in old_clauses]
            ps = [1./float(d.size) for d in ok]
            xs = [d == clause for d in ok]
            return (misc.log(sum(p for p, x in itools.izip(ps, xs) if x)) -
                    misc.log(sum(ps)))
        return -np.inf
    return give_proposal_log_p


def give_proposal_log_fb_maker(data):
    @utils.validate_syntax
    def give_proposal_log_fb(old, new, **kwargs):
        old_clauses = old.semantics.clauses
        new_clauses = new.semantics.clauses
        len_difference = len(old_clauses) - len(new_clauses)
        if len_difference == 1:
            old_set = set(old_clauses)
            new_set = set(new_clauses)
            diff = old_set - new_set
            if len(diff) == 1:
                clause = diff.pop()
                ok = [d for d in data if d not in new_clauses]
                ps = [1./float(d.size) for d in ok]
                xs = [d == clause for d in ok]
                b = (misc.log(sum(p for p, x in itools.izip(ps, xs) if x)) -
                     misc.log(sum(ps)))
                return (-np.inf, b)
        elif len_difference == -1:
            old_set = set(old_clauses)
            new_set = set(new_clauses)
            diff = new_set - old_set
            if len(diff) == 1:
                clause = diff.pop()
                ok = [d for d in data if d not in old_clauses]
                ps = [1./float(d.size) for d in ok]
                xs = [d == clause for d in ok]
                f = (misc.log(sum(p for p, x in itools.izip(ps, xs) if x)) -
                     misc.log(sum(ps)))
                return (f, -np.inf)
        return (-np.inf, -np.inf)
    return give_proposal_log_fb


class AddExceptionProposer(P.Proposer):
    """
    Proposer for adding an exception to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {e}), where e is a Rule taken
    verbatim from the initial data.
    """
    def __init__(self, data=None, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value_maker(data)
        self.give_proposal_log_fb = give_proposal_log_fb_maker(data)
        super(AddExceptionProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    import TeRF.Examples as e
    data = [e.head_datum_T,
            e.head_datum_T2,
            e.head_datum_T3]

    utils.test_a_proposer(propose_value_maker(data),
                          give_proposal_log_fb_maker(data))

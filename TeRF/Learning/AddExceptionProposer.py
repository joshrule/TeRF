import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Miscellaneous as misc


def propose_value_maker(data):
    def propose_value(value, **kwargs):
        new_value = copy.deepcopy(value)
        try:
            ok_data = [datum for datum in data if datum not in new_value]
            sizes = [datum.size for datum in ok_data]
            max_size = float(max(sizes))
            ps = [np.exp(-float(size)/max_size) for size in sizes]
            ps = [p/sum(ps) for p in ps]
            rule = copy.deepcopy(np.random.choice(ok_data, p=ps))
        except (TypeError, ValueError):
            raise P.ProposalFailedException('AddException: no new exceptions')
        print '# aep: adding rule', rule
        new_value.add(rule)
        return new_value
    return propose_value


def give_proposal_log_p_maker(data):
    def give_proposal_log_p(old, new, **kwargs):
        if old.signature == new.signature:
            rule = new.find_insertion(old)
            try:
                ok_data = [(d, d.unify(rule, type='alpha') is not None)
                           for d in data if d not in old]
                sizes = [d[0].size for d in ok_data]
                max_size = float(max(sizes))
                ps = [np.exp(-float(size)/max_size) for size in sizes]
                ps = [p/sum(ps) for p in ps]
                return misc.log(sum(p for p, d in zip(ps, ok_data) if d[1]))
                # return misc.logNof(ok_data, n=sum(ok_data))
            except (TypeError, AttributeError):
                pass
        return -np.inf
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

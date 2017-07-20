import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Miscellaneous as misc


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    rule = pu.choose_a_rule(new_value)
    diffs = rule.lhs.differences(rule.rhs0, top=False)

    try:
        lhs, rhs = diffs[np.random.choice(len(diffs))]
    except ValueError:
        raise P.ProposalFailedException('LocalDifference: no good differences')

    new_rule = pu.make_a_rule(lhs, rhs)
    print 'ldp: changing', rule, 'to', new_rule
    return new_value.swap(rule, new_rule)


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature:
        old_rule, new_rule = old.find_difference(new)
        try:
            p_rule = misc.logNof(list(old.rules()))
            diffs = old_rule.lhs.differences(old_rule.rhs0, top=False)
            p_diff = misc.logNof(diffs,
                                 n=diffs.count((new_rule.lhs, new_rule.rhs0)))
            return p_rule + p_diff
        except AttributeError:
            pass
    return -np.inf


class LocalDifferenceProposer(P.Proposer):
    """
    Proposer for modifying a rule by demoting it and adding a new head
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l' and r' are subtrees from l and r,
    respectively, such that l' and r' are different trees but occurred at the
    same position in l and r.
    """
    def __init__(self, **kwargs):
        """Create a LocalDifferenceProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(LocalDifferenceProposer, self).__init__(**kwargs)

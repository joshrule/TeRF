import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import scipy as sp
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A


def demote(t, signature, invent):
    try:
        head = np.random.choice(signature.operators.possible_roots({t}))
    except ValueError:
        raise P.ProposalFailedException('DemoteSubrule: no valid heads')
    body = [signature.sample_term(invent=invent) for _ in xrange(head.arity-1)]
    body.insert(np.random.choice(head.arity), t)
    return A.App(head, body)


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    rule = pu.choose_a_rule(new_value)
    side = np.random.choice(['lhs', 'rhs', 'both'])

    sig = value.signature.operators
    lhs = rule.lhs if side == 'rhs' else demote(rule.lhs, sig, True)

    sig.replace_vars(lhs.variables)
    rhs = rule.rhs0 if side == 'lhs' else demote(rule.rhs0, sig, True)

    new_rule = pu.make_a_rule(lhs, rhs)
    print 'dsp: changing', rule, 'to', new_rule
    return new_value.swap(rule, new_rule)


def log_p_is_demotion(r1, r2, signature, invent):
    if r1 != r2 and r1 in getattr(r2, 'body', []):
        operators = signature.operators
        p_op = misc.logNof(operators) if r2.head in operators else -np.inf

        branches = r2.body[:]
        branches.remove(r1)
        p_branches = sum([signature.log_p(b, invent=invent) for b in branches])

        p_index = misc.logNof(r2.body)

        return p_op + p_branches + p_index
    return -np.inf


def give_proposal_log_p(old, new, **kwargs):
    if old.signature == new.signature:
        old_rule, new_rule = old.find_difference(new)
        try:
            p_method = -misc.log(3)
            p_rule = misc.logNof(list(old.rules()))
            p = p_method + p_rule

            p_demote_lhs = log_p_is_demotion(old_rule.lhs, new_rule.lhs,
                                             new.signature, True)

            sig = new.signature.operators.replace_vars(new_rule.lhs.variables)
            p_demote_rhs = log_p_is_demotion(old_rule.rhs0, new_rule.rhs0,
                                             sig, False)

            p_lhs = (p + p_demote_lhs) if p_demote_rhs == -np.inf else -np.inf
            p_rhs = (p + p_demote_rhs) if p_demote_lhs == -np.inf else -np.inf
            p_both = p + p_demote_lhs + p_demote_rhs

            return sp.misc.logsumexp([p_lhs, p_rhs, p_both])
        except AttributeError:
            pass
    return -np.inf


class DemoteSubruleProposer(P.Proposer):
    """
    Proposer for modifying a rule by demoting it and adding a new head
    (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r'. l is an immediate subtree of l', and r of r'.
    """
    def __init__(self, **kwargs):
        """Create a DemoteSubruleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(DemoteSubruleProposer, self).__init__(**kwargs)

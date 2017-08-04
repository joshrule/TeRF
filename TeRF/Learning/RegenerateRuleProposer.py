import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import scipy.misc as sm
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Miscellaneous as misc


def propose_value_maker(p_r):
    def propose_value(value, **kwargs):
        new_value = copy.deepcopy(value)
        rule = pu.choose_a_rule(new_value)
        side = np.random.choice(['lhs', 'rhs', 'both'])

        lhs = rule.lhs
        sig = new_value.signature.operators
        if side != 'rhs':
            while lhs == rule.lhs:
                lhs = sig.sample_term_t(rule.lhs, p_r, invent=True)

        old_rhs = np.random.choice(list(rule.rhs))
        rhs = old_rhs
        if side != 'lhs':
            sig.replace_vars(lhs.variables)
            while rhs == old_rhs:
                rhs = sig.sample_term_t(rhs, p_r, invent=False)

        new_rule = pu.make_a_rule(lhs, rhs)
        print '# rrp: changing', rule, 'to', new_rule
        return new_value.swap(rule, new_rule)
    return propose_value


def give_proposal_log_p_maker(p_r):
    def give_proposal_log_p(old, new, **kwargs):
        if old.signature == new.signature:
            new_rule, old_rule = new.find_difference(old)
            try:
                p_method = -misc.log(3)
                p_rule = misc.logNof(list(new.rules()))
                p = p_method + p_rule
                sig = new.signature.operators
                p_regen_lhs = sig.log_p_t(new_rule.lhs, old_rule.lhs,
                                          p_r, invent=True)
                sig.replace_vars(new_rule.lhs.variables)
                p_regen_rhs = sig.log_p_t(new_rule.rhs0, old_rule.rhs0,
                                          p_r, invent=False)

                p_lhs = (p+p_regen_lhs) if p_regen_rhs == -np.inf else -np.inf
                p_rhs = (p+p_regen_rhs) if p_regen_lhs == -np.inf else -np.inf
                p_both = p + p_regen_lhs + p_regen_rhs

                return sm.logsumexp([p_lhs, p_rhs, p_both])
            except AttributeError:
                pass
        return -np.inf
    return give_proposal_log_p


class RegenerateRuleProposer(P.Proposer):
    """
    Proposer for regenerating the LHS of a TRS rule (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r. The LHS is resampled, but the RHS is unchanged.
    """
    def __init__(self, p_r=0.2, **kwargs):
        """
        Create a RegenerateLHSProposer

        Args:
          p_r: float, the probability of regenerating a subterm (subterms
              of a regenerated term are not considered for regeneration).
        """
        self.propose_value = propose_value_maker(p_r),
        self.give_proposal_log_p = give_proposal_log_p_maker(p_r),
        super(RegenerateRuleProposer, self).__init__(**kwargs)

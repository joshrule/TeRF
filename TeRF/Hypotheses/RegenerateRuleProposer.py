from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log, inf
from numpy.random import choice
from scipy.misc import logsumexp

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Miscellaneous import find_difference, log1of
from TeRF.Utilities import sample_term_t, log_p_t


def propose_value_maker(p_r):
    def propose_value(value, **kwargs):
        new_value = deepcopy(value)
        try:
            idx = choice(len(new_value.rules))
            rule = new_value.rules[idx]
        except ValueError:
            raise ProposalFailedException('RegenerateLHSProposer: ' +
                                          'TRS must have rules')
        side = choice(['lhs', 'rhs', 'both'])
        try:
            new_lhs = rule.lhs
            if side != 'rhs':
                lhs_signature = new_value.operators | new_value.variables
                while new_lhs == rule.lhs:
                    new_lhs = sample_term_t(lhs_signature, rule.lhs, p_r)

            new_rhs = rule.rhs
            if side != 'lhs':
                rhs_signature = new_value.operators | new_lhs.variables()
                while new_rhs == rule.rhs:
                    new_rhs = sample_term_t(rhs_signature, rule.rhs, p_r)

            new_rule = RewriteRule(new_lhs, new_rhs)
        except TRSError:
            raise ProposalFailedException('RegenerateLHSProposer: bad rule')
        # print 'rrp: changing', rule, 'to', new_rule
        new_value.rules[idx] = new_rule
        return new_value
    return propose_value


def give_proposal_log_p_maker(p_r):
    def give_proposal_log_p(old, new, **kwargs):
        if old.variables == new.variables and old.operators == new.operators:
            old_rule, new_rule = find_difference(old.rules, new.rules)
            try:
                p_method = -log(3)
                p_rule = log1of(new.rules)
                lhs_signature = new.operators | new.variables
                p_regen_lhs = log_p_t(new_rule.lhs, lhs_signature,
                                      old_rule.lhs, p_r)
                rhs_signature = new.operators | new_rule.lhs.variables()
                p_regen_rhs = log_p_t(new_rule.rhs, rhs_signature,
                                      old_rule.rhs, p_r)

                p_lhs = log(0)
                if p_regen_rhs == -inf:
                    p_lhs = p_method + p_rule + p_regen_lhs

                p_rhs = log(0)
                if p_regen_lhs == -inf:
                    p_rhs = p_method + p_rule + p_regen_rhs

                p_both = p_method + p_rule + p_regen_lhs + p_regen_rhs

                return logsumexp([p_lhs, p_rhs, p_both])
            except AttributeError:
                pass
        return log(0)
    return give_proposal_log_p


class RegenerateRuleProposer(Proposer):
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

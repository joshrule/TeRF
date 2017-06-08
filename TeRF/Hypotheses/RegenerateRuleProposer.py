from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Miscellaneous import find_difference
from TeRF.Utilities import sample_term_t, log_p_t


def propose_value_maker(p_r):
    def propose_value(value, **kwargs):
        new_value = deepcopy(value)
        try:
            rule = choice(new_value.rules)
        except ValueError:
            raise ProposalFailedException('RegenerateLHSProposer: ' +
                                          'TRS must have rules')
        try:
            lhs_signature = new_value.operators | new_value.variables
            new_lhs = sample_term_t(lhs_signature, rule.lhs, p_r)
            rhs_signature = new_value.operators | new_lhs.variables()
            new_rhs = sample_term_t(rhs_signature, rule.rhs, p_r)
            new_rule = RewriteRule(new_lhs, new_rhs)
        except TRSError:
            raise ProposalFailedException('RegenerateLHSProposer: bad rule')
        new_value.del_rule(rule)
        return new_value.add_rule(new_rule)
    return propose_value


def give_proposal_log_p_maker(p_r):
    def give_proposal_log_p(old, new, **kwargs):
        if old.variables == new.variables and old.operators == new.operators:
            old_rule, new_rule = find_difference(old.rules, new.rules)
            try:
                p_choosing_rule = -log(len(new.rules))
                lhs_signature = new.operators | new.variables
                p_lhs = log_p_t(new_rule.lhs, lhs_signature, old_rule.lhs, p_r)
                rhs_signature = new.operators | new_rule.lhs.variables()
                p_rhs = log_p_t(new_rule.rhs, rhs_signature, old_rule.rhs, p_r)
                return p_choosing_rule + p_lhs + p_rhs
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

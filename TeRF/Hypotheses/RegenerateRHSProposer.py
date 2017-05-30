from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Utilities import sample_term_t, log_p_t


def propose_value_maker(p_r):
    def propose_value(value, **kwargs):
        new_value = deepcopy(value)
        try:
            rule = choice(new_value.rules)
        except ValueError:
            raise ProposalFailedException('RegenerateRHSProposer: ' +
                                          'TRS must have rules')
        try:
            signature = new_value.operators | rule.lhs.variables()
            new_rhs = sample_term_t(signature, rule.rhs, p_r)
            new_rule = RewriteRule(rule.lhs, new_rhs)
        except TRSError:
            raise ProposalFailedException('RegenerateRHSProposer: ' +
                                          'bad rule')
        new_value.del_rule(rule)
        # print 'proposing to make {} into {}'.format(rule, new_rule)
        return new_value.add_rule(new_rule)
    return propose_value


def give_proposal_log_p_maker(p_r):
    def give_proposal_log_p(old, new, **kwargs):
        if old.variables == new.variables and \
           old.operators == new.operators:
            old_rule, new_rule = None, None
            for o, n in zip(old.rules, new.rules):
                if o != n and old_rule is None:
                    old_rule = o
                    new_rule = n
                elif o != n:
                    return log(0)
            if old_rule is None:
                return log(0)
            signature = new.operators | new_rule.lhs.variables()
            return log_p_t(new_rule.rhs, signature, old_rule.rhs, p_r)
        else:
            return log(0)
    return give_proposal_log_p


class RegenerateRHSProposer(Proposer):
    """
    Proposer for regenerating the RHS of a TRS rule (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l -> r'. The LHS is unchanged, but the RHS is resampled.
    """
    def __init__(self, p_r=0.2, **kwargs):
        """
        Create a RegenerateRHSProposer

        Args:
          p_r: float, the probability of regenerating a subterm (subterms
              of a regenerated term are not considered for regeneration).
        """
        super(RegenerateRHSProposer, self).__init__(
            propose_value=propose_value_maker(p_r),
            give_proposal_log_p=give_proposal_log_p_maker(p_r),
            **kwargs)

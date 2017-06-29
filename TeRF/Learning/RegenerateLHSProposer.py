from copy import deepcopy
from LOTlib.Hypotheses.Proposers.Proposer import (Proposer,
                                                  ProposalFailedException)
from numpy import log
from numpy.random import choice

from TeRF.TRS import RewriteRule, TRSError
from TeRF.Utilities import sample_term_tc, log_p_tc


def propose_value_maker(p_r):
    def propose_value(value, **kwargs):
        new_value = deepcopy(value)
        try:
            rule = choice(new_value.rules)
        except ValueError:
            raise ProposalFailedException('RegenerateLHSProposer: ' +
                                          'TRS must have rules')
        try:
            new_lhs = sample_term_tc(new_value.operators | new_value.variables,
                                     rule.lhs, p_r,
                                     rule.rhs.variables())
            new_rule = RewriteRule(new_lhs, rule.rhs)
        except TRSError:
            raise ProposalFailedException('RegenerateLHSProposer: ' +
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
            return log_p_tc(new_rule.rhs, signature, old_rule.rhs, p_r,
                            old_rule.rhs.variables())
        else:
            return log(0)
    return give_proposal_log_p


class RegenerateLHSProposer(Proposer):
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
        super(RegenerateLHSProposer, self).__init__(
            propose_value=propose_value_maker(p_r),
            give_proposal_log_p=give_proposal_log_p_maker(p_r),
            **kwargs)

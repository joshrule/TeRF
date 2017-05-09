from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from copy import copy
from numpy.random import choice
from numpy import log
from TRS.Utilities import sample_term_t, log_p_t
from TRS import RewriteRule, TRSError, Op


class RegenerateRHSProposer(Proposer):
    """
    Proposer for regenerating the RHS of a TRS rule (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l -> r'. The LHS is unchanged, but the RHS is resampled.
    """
    def __init__(p_r=0.2, **kwargs):
        """
        Create a RegenerateRHSProposer

        Args:
          p_r: float, the probability of regenerating a subterm (subterms
              of a regenerated term are not considered for regeneration).
        """
        def propose_value(value, **kwargs):
            new_value = copy(value)
            try:
                rule = choice(new_value.rules)
            except ValueError:
                raise ProposalFailedException('RegenerateRHSProposer: ' +
                                              'TRS must have rules')
            try:
                signature = [s for s in new_value.signature
                             if isinstance(s, Op)] + rule.lhs.variables
                new_rhs = sample_term_t(signature, rule.rhs, p_r)
                new_rule = RewriteRule(rule.lhs, new_rhs)
            except TRSError:
                raise ProposalFailedException('RegenerateRHSProposer: ' +
                                              'bad rule')
            new_value.del_rule(rule)
            return new_value.add_rule(new_rule)

        def give_proposal_log_p(old, new, **kwargs):
            if old.signature == new.signature:
                for o, n in zip(old.rules, new.rules):
                    if o != n and 'old_rule' not in locals():
                        old_rule = o
                        new_rule = n
                    else:
                        return log(0)
                signature = new.signature + new_rule.lhs.variables
                return log_p_t(new_rule.rhs, signature, old_rule.rhs, p_r)
            else:
                return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

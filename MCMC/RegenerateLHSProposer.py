from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from copy import copy
from numpy.random import choice
from numpy import log
from TRS.Utilities import sample_term_tc, log_p_tc
from TRS import RewriteRule, TRSError


class RegenerateLHSProposer(Proposer):
    """
    Proposer for regenerating the LHS of a TRS rule (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {x}), give a new TRS (S, R U {x'}), where x is a rule,
    l -> r,  and x' is l' -> r. The LHS is resampled, but the RHS is unchanged.
    """
    def __init__(p_r=0.2, **kwargs):
        """
        Create a RegenerateLHSProposer

        Args:
          p_r: float, the probability of regenerating a subterm (subterms
              of a regenerated term are not considered for regeneration).
        """
        def propose_value(value, **kwargs):
            new_value = copy(value)
            try:
                rule = choice(new_value.rules)
            except ValueError:
                raise ProposalFailedException('RegenerateLHSProposer: ' +
                                              'TRS must have rules')
            try:
                signature = new_value.signature  # can include any variable
                new_lhs = sample_term_tc(signature, rule.lhs, p_r,
                                         rule.rhs.variables)
                new_rule = RewriteRule(new_lhs, rule.rhs)
            except TRSError:
                raise ProposalFailedException('RegenerateLHSProposer: ' +
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
                return log_p_tc(new_rule.rhs, signature, old_rule.rhs, p_r,
                                old_rule.rhs.variables)
            else:
                return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

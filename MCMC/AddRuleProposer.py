from LOTlib.Hypotheses.Proposers.TRS.Proposer import (Proposer,
                                                      ProposalFailedException)
from copy import copy
from numpy import log
from TRS.Utilities import sample_term, log_p
from TRS import RewriteRule, TRSError, Op, Var


class AddRuleProposer(Proposer):
    """
    Proposer for adding a RewriteRule to a TRS (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R), give a new TRS (S, R U {x}), where x is a rule, l -> r
    """
    def __init__(**kwargs):
        """Create a NewRuleProposer"""
        def propose_value(value, **kwargs):
            new_value = copy(value)
            try:
                lhs = None
                while lhs is None or isinstance(lhs, Var):
                    lhs = sample_term(value.signature)
                rhs_signature = [s for s in value.signature
                                 if isinstance(s, Op)] + lhs.variables
                rhs = sample_term(rhs_signature)
                new_rule = RewriteRule(lhs, rhs)
            except TRSError:
                raise ProposalFailedException('RegenerateRHSProposer: ' +
                                              'couldn\'t generate new rule')
            return new_value.add_rule(new_rule)

        def give_proposal_log_p(old, new, **kwargs):
            if len(old.rules) == len(new.rules)-1 and \
               old.rules == new.rules[:-1] and \
               old.signature == new.signature:
                rule = new.rules[:-1]
                p_lhs = log_p(rule.lhs, new.signature)
                rhs_signature = new.signature + rule.lhs.variables
                p_rhs = log_p(rule.rhs, rhs_signature)
                return (p_lhs + p_rhs)
            else:
                return log(0)

        Proposer.__init__(propose_value=propose_value,
                          give_proposal_log_p=give_proposal_log_p,
                          **kwargs)

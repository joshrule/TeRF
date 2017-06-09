from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer

import TeRF.Hypotheses.AddRuleProposer as arp
import TeRF.Hypotheses.DeleteRuleProposer as drp

import TeRF.Hypotheses.AddOperatorRuleProposer as aorp
import TeRF.Hypotheses.DeleteOperatorProposer as dop

import TeRF.Hypotheses.AddVariableRuleProposer as avrp
import TeRF.Hypotheses.DeleteVariableProposer as dvp

import TeRF.Hypotheses.RegenerateRuleProposer as rrp
import TeRF.Hypotheses.PromoteSubruleProposer as psp
import TeRF.Hypotheses.SwapSubruleProposer as ssp


class TRSTestProposer(MixtureProposer):
    def __init__(self, p_arity=0.0, gensym=None, p_r=0.0,
                 privileged_ops=None, p_rules=0.0, **kwargs):
        proposal_fns = [
            (aorp.propose_value_maker(gensym, p_arity, p_rules),
             aorp.give_proposal_log_p_maker(p_arity, p_rules)),
            (avrp.propose_value_maker(gensym, p_rules),
             avrp.give_proposal_log_p_maker(p_rules)),
            (arp.propose_value,
             arp.give_proposal_log_p),
            (dop.propose_value_maker(privileged_ops),
             dop.give_proposal_log_p),
            (dvp.propose_value,
             dvp.give_proposal_log_p),
            (drp.propose_value,
             drp.give_proposal_log_p),
            (rrp.propose_value_maker(p_r),
             rrp.give_proposal_log_p_maker(p_r)),
            (psp.propose_value,
             psp.give_proposal_log_p),
            (ssp.propose_value,
             ssp.give_proposal_log_p)
        ]

        weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(TRSTestProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

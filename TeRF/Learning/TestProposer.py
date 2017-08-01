from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer

import TeRF.Learning.AddRuleProposer as arp
import TeRF.Learning.DeleteRuleProposer as drp
import TeRF.Learning.RegenerateRuleProposer as rrp
import TeRF.Learning.PromoteSubruleProposer as psp
import TeRF.Learning.SwapSubruleProposer as ssp
import TeRF.Learning.DemoteSubruleProposer as dsp
import TeRF.Learning.LocalDifferenceProposer as ldp
import TeRF.Learning.MoveRuleProposer as mrp
import TeRF.Learning.ReplaceWithVariableProposer as rvp
# import TeRF.Learning.NewTRSProposer as ntp


class TestProposer(MixtureProposer):
    def __init__(self, p_arity=0.0, gensym=None, p_r=0.0,
                 privileged_ops=None, p_rules=0.0, **kwargs):
        proposal_fns = [
            (arp.propose_value,
             arp.give_proposal_log_p),
            (drp.propose_value,
             drp.give_proposal_log_p),
            (rrp.propose_value_maker(p_r),
             rrp.give_proposal_log_p_maker(p_r)),
            (psp.propose_value,
             psp.give_proposal_log_p),
            (ssp.propose_value,
             ssp.give_proposal_log_p),
            (dsp.propose_value,
             dsp.give_proposal_log_p),
            (ldp.propose_value,
             ldp.give_proposal_log_p),
            (mrp.propose_value,
             mrp.give_proposal_log_p),
            (rvp.propose_value,
             rvp.give_proposal_log_p)
            # (ntp.propose_value_maker(p_rules),
            #  ntp.give_proposal_log_p_maker(p_rules))
        ]

        weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(TestProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

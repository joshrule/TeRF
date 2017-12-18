from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer

import TeRF.Learning.AddRuleProposer as arp
import TeRF.Learning.DeleteRuleProposer as drp
import TeRF.Learning.RegenerateRuleProposer as rrp
import TeRF.Learning.MoveRuleProposer as mrp
import TeRF.Learning.AddExceptionProposer as aep


class TestProposer(MixtureProposer):
    def __init__(self, data=None, **kwargs):
        proposal_fns = [
            (arp.propose_value,
             arp.give_proposal_log_p),
            (drp.propose_value,
             drp.give_proposal_log_p),
            (rrp.propose_value,
             rrp.give_proposal_log_p),
            (mrp.propose_value,
             mrp.give_proposal_log_p),
            (aep.propose_value_maker(data),
             aep.give_proposal_log_p_maker(data))
        ]

        weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(TestProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

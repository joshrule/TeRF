from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer

import TeRF.Hypotheses.AddRuleProposer as arp
import TeRF.Hypotheses.DeleteRuleProposer as drp


class TRSLowLevelProposer(MixtureProposer):
    def __init__(self, p_arity=0.0, gensym=None, p_r=0.0,
                 privileged_ops=None, **kwargs):
        proposal_fns = [
            (arp.propose_value,
             arp.give_proposal_log_p),
            (drp.propose_value,
             drp.give_proposal_log_p)
        ]

        weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(TRSLowLevelProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer
# import TeRF.Miscellaneous as misc
import TeRF.Learning.AddRuleProposer as arp
import TeRF.Learning.DeleteRuleProposer as drp
# import TeRF.Learning.RegenerateRuleProposer as rrp
# import TeRF.Learning.MoveRuleProposer as mrp
# import TeRF.Learning.AddExceptionProposer as aep
# import TeRF.Learning.ReplaceWithVariableProposer as rvp


class LOTProposer(MixtureProposer):
    def __init__(self, data=None, templates=None, **kwargs):
        proposal_fns = [
            (arp.propose_value_maker(templates),
             arp.give_proposal_log_fb_maker(templates)),
            (drp.propose_value,
             drp.give_proposal_log_fb),
            # (rrp.propose_value,
            #  rrp.give_proposal_log_fb),
            # (mrp.propose_value,
            #  mrp.give_proposal_log_fb),
            # (aep.propose_value_maker(data),
            #  aep.give_proposal_log_fb_maker(data)),
            # (rvp.propose_value,
            #  rvp.give_proposal_log_fb)
        ]

        weights = [0.5, 0.5]
        # weights = misc.renormalize([3, 4, 3, 1, 1, 2])
        # weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(LOTProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

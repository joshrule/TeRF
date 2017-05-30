from LOTlib.Hypotheses.Proposers.MixtureProposer import MixtureProposer

import TeRF.Hypotheses.AddRuleProposer as arp
import TeRF.Hypotheses.AddOperatorProposer as aop
import TeRF.Hypotheses.AddVariableProposer as avp
import TeRF.Hypotheses.DeleteRuleProposer as drp
import TeRF.Hypotheses.DeleteOperatorProposer as dop
import TeRF.Hypotheses.DeleteVariableProposer as dvp
import TeRF.Hypotheses.RegenerateLHSProposer as rlp
import TeRF.Hypotheses.RegenerateRHSProposer as rrp


class TRSUnrestrictedProposer(MixtureProposer):
    def __init__(self, p_arity=0.0, gensym=None, p_r=0.0, **kwargs):
        proposal_fns = [
            (aop.propose_value_maker(gensym, p_arity),
             aop.give_proposal_log_p_maker(p_arity)),
            (avp.propose_value_maker(gensym),
             avp.give_proposal_log_p),
            (arp.propose_value,
             arp.give_proposal_log_p),
            (dop.propose_value,
             dop.give_proposal_log_p),
            (dvp.propose_value,
             dvp.give_proposal_log_p),
            (drp.propose_value,
             drp.give_proposal_log_p),
            (rlp.propose_value_maker(p_r),
             rlp.give_proposal_log_p_maker(p_r)),
            (rrp.propose_value_maker(p_r),
             rrp.give_proposal_log_p_maker(p_r))
        ]

        weights = [1.0/len(proposal_fns)]*len(proposal_fns)

        super(TRSUnrestrictedProposer, self).__init__(
            proposal_fns=proposal_fns, weights=weights, **kwargs)

"""Generic Proposer class and associated exception

Proposer defines propose, a function for generating new MCMC proposals. It
takes as arguments functions which generate the newly proposed values, and
functions which compute the probabilities of specific types of proposals.
propose itself allows access to these various computations by means of its
arguments.

ProposalFailedException signals a failed attempt to generate a proposal.
"""


class ProposalFailedException(Exception):
    """Raise this when a proposer fails to generate a proposal"""
    pass


class Proposer(object):
    """generic parent for Proposer classes"""
    def __init__(self, propose_value=None, give_proposal_log_p=None, **kwargs):
        """create the proposer:

        propose_value(v) generates a newly proposed value v' from v

        give_proposal_log_p(v,v') gives the probability of proposing v' from v
        """
        def propose(self, ret='both', newVal=None, **kwargs):
            """generate a proposal and compute its probability"""
            while newVal is None:
                try:
                    newVal = propose_value(self.value, **kwargs)
                except ProposalFailedException:
                    pass

            hypothesis = self.__copy__(value=newVal)

            # the return value depends on 'ret'
            if ret == 'value':
                return hypothesis
            else:
                logp = give_proposal_log_p(self.value, newVal, **kwargs)
                if ret == 'logp':
                    return logp
                else:
                    fb = logp - \
                         give_proposal_log_p(newVal, self.value, **kwargs)
                    if ret == 'fb':
                        return fb
                    else:
                        return hypothesis, fb, logp

        self.propose = propose

        def __call__(self, **kwargs):
            return self.propose(**kwargs)

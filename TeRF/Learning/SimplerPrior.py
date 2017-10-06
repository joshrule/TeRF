import LOTlib.Miscellaneous as misc


class TRSPrior(object):
    @misc.attrmem('prior')
    def compute_prior(self):
        """
        the log prior of a TRSHypothesis

        TRSPrior is sensitive to the number of nodes in the rules of the TRS:
        e ^( - {\sum_{rules} #_nodes_in(rule.lhs) + #_nodes_in(rule.rhs) )

        It should be part of a TeRF.Learning.TRSHypothesis.
        
        Returns
        -------
        float
            -inf <= x <= 0, log p(self.value)

        Notes
        -----
        - We add 1 so that the empty TRS doesn't have log_p = 0
        - We could add some constant multiplier to reduce the cost of each node
        - We could perform inference over that multiplier
        - We could increase complexity (see GenerativePrior.py for an example)
        """
        return - (1 + self.value.size) / self.prior_temperature

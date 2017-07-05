class TRSSimplePrior(object):
    def compute_prior(self):
        """
        the log prior of the hypothesis

        TRSSimplePrior is based entirely on the /size/ of the TRS:
        # operators + # rules + # nodes in each rule (lhs + rhss)

        Given the assumptions below, it should be part of a LOTlib Hypothesis.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.prior_temperature: from LOTlib.Hypotheses.Hypothesis
        Returns: a float, -inf <= x <= 0, log p(self.value)
        """
        return -len(self.value) / self.prior_temperature

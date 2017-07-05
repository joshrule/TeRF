from TeRF.Types.Trace import rewrites_to


class TRSLikelihood(object):
    def compute_single_likelihood(self, datum):
        """
        the log likelihood of the hypothesis for a single datum

        This likelihood is generative. It asks how likely datum.lhs is to be
        generated from self.start and how likely datum.rhs is to be generated
        from datum.lhs given the rules and our assumptions about observation
        frequency.

        It ignores self.likelihood_temperature; compute_likelihood manages it.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.p_observe: should be an argument to the hypothesis __init__
          self.start: the starting term
        Args:
          datum: a rewriteRule representing a single datum
        Returns: a float, -inf <= x <= 0, log p(datum | self.value)
        """
        lhs = datum.lhs
        rhs = datum.rhs
        start = self.start
        p_lhs = rewrites_to(self.value, lhs, start, self.p_observe, steps=10)
        p_rhs = rewrites_to(self.value, rhs, lhs, self.p_observe, steps=10)
        return p_lhs + p_rhs

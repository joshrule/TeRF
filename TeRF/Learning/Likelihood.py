from TeRF.Types import Trace


class Likelihood(object):
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
        p_lhs = Trace(self.value, self.start, p_observe=self.p_observe,
                      max_steps=10).rewrites_to(datum.lhs)
        p_rhs = Trace(self.value, datum.lhs, p_observe=self.p_observe,
                      max_steps=10).rewrites_to(datum.rhs)
        return p_lhs + p_rhs

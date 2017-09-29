import numpy as np
import TeRF.Types.Trace as T


class Likelihood(object):
    def compute_single_likelihood(self, datum):
        """
        the log likelihood of the hypothesis for a single datum

        This likelihood is semi-generative. It assumes the existence of
        datum.lhs and then asks how likely datum.rhs0 is to be generated
        from datum.lhs given the rules and assumed observation frequency.

        compute_likelihood manages likelihood_temperature. It's ignored here.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.p_partial: should be an argument of the hypothesis
        Args:
          datum: a rewriteRule representing a single datum
        Returns: a float, -inf <= x <= 0, log p(datum | self.value)
        """
        t = T.Trace(self.value, datum.lhs, p_observe=0.0,
                    max_steps=100).run()
        ll = t.rewrites_to(datum.rhs0)

        partial_credit = self.p_partial + (self.temperature - 1.0
                                           if self.temperature > 1.0
                                           else 0.0)

        if ll == -np.inf:
            return np.log(partial_credit)
        else:
            return np.log(1.-partial_credit) + ll

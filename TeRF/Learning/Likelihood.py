import numpy as np
import scipy as sp
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
          self.p_observe: should be an argument to the hypothesis __init__
          self.start: the starting term
        Args:
          datum: a rewriteRule representing a single datum
        Returns: a float, -inf <= x <= 0, log p(datum | self.value)
        """
        rt = T.Trace(self.value, datum.lhs, p_observe=self.p_observe,
                     max_steps=5).run()
        p_eval = rt.rewrites_to(datum.rhs0)
        p_gen = self.value.signature.log_p(datum.rhs0, invent=False)
        return sp.misc.logsumexp([np.log(self.p_similar) + p_eval,
                                  np.log(1-self.p_similar) + p_gen])

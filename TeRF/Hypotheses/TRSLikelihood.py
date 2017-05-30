from scipy.stats import geom, bernoulli

from TeRF.Utilities import log_p, rewrites_to


class TRSLikelihood(object):
    def compute_single_likelihood(self, datum):
        """
        the log likelihood of the hypothesis for a single datum

        This likelihood is generative. It asks how likely datum.lhs is to be
        sampled from the value's signature and how likely datum.rhs is to be
        observed as a successor to datum.lhs given the rules, our assumptions
        about observation frequency, and how similar two trees need to be to
        count as an observation.

        It ignores self.likelihood_temperature; compute_likelihood manages it.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.p_observe: should be an argument to the hypothesis __init__
          self.p_similar: should be an argument to the hypothesis __init__
        Args:
          datum: a rewriteRule representing a single datum
        Returns: a float, -inf <= x <= 0, log p(datum | self.value)
        """
        p_gen_lhs = log_p(datum.lhs, self.value.variables |
                          self.value.operators)
        min_step, min_dist, nf_step = rewrites_to(self.value,
                                                  datum.lhs,
                                                  datum.rhs,
                                                  steps=10)
        if min_step == nf_step:
            p_eval_rhs = geom.logsf(k=min_step, p=self.p_observe)
        else:
            p_eval_rhs = geom.logpmf(k=min_step+1, p=self.p_observe)
        # p_distance = geom.logpmf(k=min_dist+1, p=self.p_similar)
        p_distance = bernoulli.logpmf(k=min_dist, p=(1-self.p_similar))
        return p_gen_lhs + p_eval_rhs + p_distance

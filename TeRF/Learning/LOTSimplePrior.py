import numpy as np
import LOTlib.Miscellaneous as misc


class LOTSimplePrior(object):
    @misc.attrmem('prior')
    def compute_prior(self):
        """
        the log prior of the hypothesis' semantic grammar.

        Notes
        -----
        - This prior focuses exclusively on the semantic grammar but should be
          adapted as learning increases to consider the syntax.
        - Given the assumptions below, use it as part of a TeRF LOTHypothesis.

        Assumes
        -------
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.prior_temperature: from LOTlib.Hypotheses.Hypothesis
          self.p_rule: should be an argument to hypothesis' __init__
        Returns
        -------
        float
            -inf <= x <= 0, ln p(self.value)
        """
        raw_prior = -self.value.size
        temped_prior = raw_prior / (10*self.temperature+1)
        return temped_prior / self.prior_temperature


if __name__ == '__main__':
    import TeRF.Examples as tg

    prior = LOTSimplePrior()
    prior.prior_temperature = 1.0
    prior.p_rule = 0.5

    def test_prior(hypothesis):
            prior.value = hypothesis
            print '\nhypothesis:\n', prior.value
            log_p = prior.compute_prior()
            print '\nprior:\n', log_p
            print '\n1/exp(prior):\n', 1./np.exp(log_p)

    # should give -9.93962659915, or 20736.0
    lot_with_vars = tg.head_lot
    test_prior(lot_with_vars)

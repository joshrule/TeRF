import LOTlib.Miscellaneous as misc
import RobustGrammarSampler


class Prior(object):
    """
    a robust (Rational Rules-like) prior over Grammars.

    See (Goodman, Tenenbaum, Feldman, Griffiths, 2008) for the inspiration.

    Parameters
    ----------
    rrAlpha : float
        the pseudocount to use for the prior
    """
    def __init__(self, priorAlpha=1.0, **kwargs):
        self.priorAlpha = priorAlpha
        super(Prior, self).__init__(**kwargs)

    @misc.attrmem('prior')
    def compute_prior(self):
        """
        the log prior of the hypothesis' semantic grammar.

        Notes
        -----
        - This prior focuses exclusively on the semantic grammar but should be
          adapted as learning increases to consider the other grammars. It
          should assume a way to sample the LOT from scratch by first sampling
          the primitive grammar, then the syntax, then the semantics.

        Given the assumptions below, it should be part of a TeRF LOTHypothesis.

        Assumes
        -------
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.prior_temperature: from LOTlib.Hypotheses.Hypothesis
          self.p_rules: should be an argument to hypothesis' __init__

        Returns
        -------
        float
            -inf <= x <= 0, ln p(self.value)
        """
        raw_prior = RobustGrammarSampler.log_p_g(source=self.value.syntax,
                                                 target=self.value.semantics,
                                                 p_rule=self.p_rules,
                                                 alpha=self.priorAlpha)
        return raw_prior / self.prior_temperature

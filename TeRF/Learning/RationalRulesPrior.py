import LOTlib.Miscellaneous as misc
import TeRF.Learning.RationalRulesTRSGrammar as RR


class RationalRulesPrior(object):
    """
    a Rational Rules prior over TRSs.

    See (Goodman, Tenenbaum, Feldman, Griffiths, 2008) for the inspiration.

    Parameters
    ----------
    rrAlpha : float
        the pseudocount to use for the Rational Rules prior
    """
    def __init__(self, rrAlpha=1.0, **kwargs):
        self.rrAlpha = rrAlpha
        super(RationalRulesPrior, self).__init__(**kwargs)

    @misc.attrmem('prior')
    def compute_prior(self):
        """
        Rational Rules prior

        Returns
        -------
        float
            the log prior probability of a TRS
        """
        grammar = RR.RationalRulesTRSGrammar(self.value.signature.operators,
                                             alpha=self.rrAlpha)
        raw_prior = grammar.log_p_trs(self.value, self.p_rules)
        return raw_prior / self.prior_temperature

import LOTlib.Miscellaneous as misc
import TeRF.Types.RationalRulesGrammar as RRG


class RationalRulesPrior(object):
    """
    a Rational Rules prior over TRSs.

    See (Goodman, Tenenbaum, Feldman, Griffiths, 2008) for the inspiration.
    """
    @misc.attrmem('prior')
    def compute_prior(self):
        """
        Rational Rules prior

        Returns
        -------
        float
            the log prior probability of a TRS
        """
        grammar = RRG.RationalRulesGrammar(self.value.signature.operators,
                                           alpha=getattr(self, 'rrAlpha', 1.0))

        return grammar.log_p_trs(self.value) / self.prior_temperature

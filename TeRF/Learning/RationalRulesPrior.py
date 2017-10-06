import LOTlib.Miscellaneous as misc
import numpy as np
import itertools as ittl


class RationalRulesPrior(object):
    """
    a Rational Rules prior over TRSs.

    See (Goodman, Tenenbaum, Feldman, Griffiths, 2008) for details.
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

        alpha = getattr(self, 'rrAlpha', 1.0)
        terms = ittl.chain(*[[r.lhs] + list(r.rhs) for r in self.value])

        # We don't iterate, as signatures imply flat grammars
        c = self.value.signature.get_counts(terms).values()
        theprior = np.repeat(alpha, len(c))
        lp = (misc.beta(c+theprior) - misc.beta(theprior))

        return lp / self.prior_temperature

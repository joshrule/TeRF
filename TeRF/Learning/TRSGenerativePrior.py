from LOTlib.Miscellaneous import attrmem
from scipy.stats import geom

from TeRF.Types import Signature


class TRSGenerativePrior(object):

    @attrmem('prior')
    def compute_prior(self):
        """
        the log prior of the hypothesis

        This prior assumes a way to sample the TRS from scratch. Sample some
        number of operators, each with their arity, and then sample some number
        of rules and their constituent LHS and RHS(s).

        Given the assumptions below, it should be part of a TRSHypothesis.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.prior_temperature: from LOTlib.Hypotheses.Hypothesis
          self.p_operators: should be an argument to hypothesis' __init__
          self.p_arity: should be an argument to hypothesis' __init__
          self.p_rules: should be an argument to hypothesis' __init__
        Returns: a float, -inf <= x <= 0, log p(self.value)
        """
        trs = self.value
        n_operators = len(trs.operators)+1
        total_arity = sum([op.arity+1 for op in trs.operators])
        n_rules = len(trs.rules)+1
        p_rules = 0.0
        for r in self.value.rules:
            p_rules += Signature(trs.operators).log_p(r.lhs, invent=True)
            rhs_signature = Signature(trs.operators | r.lhs.variables())
            p_rules += [rhs_signature.log_p(t, invent=False) for t in r.rhs]
        return (geom.logpmf(k=n_operators, p=self.p_operators) +
                geom.logpmf(k=total_arity, p=self.p_arity) +
                geom.logpmf(k=n_rules, p=self.p_rules) +
                p_rules) / self.prior_temperature

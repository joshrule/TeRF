from LOTlib.Miscellaneous import attrmem
from scipy.stats import geom

from TeRF.Utilities import log_p


class TRSGenerativePrior(object):
    
    @attrmem('prior')
    def compute_prior(self):
        """
        the log prior of the hypothesis

        This prior assumes a way to sample the TRS from wholecloth. Sample some
        number of operators, each with their arity, and then some number of
        variables. Finally, sample some number of rules and sample trees for
        each rule.

        Given the assumptions below, it should be part of a TRSHypothesis.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.prior_temperature: from LOTlib.Hypotheses.Hypothesis
          self.p_operators: should be an argument to hypothesis' __init__
          self.p_arity: should be an argument to hypothesis' __init__
          self.p_variables: should be an argument to hypothesis' __init__
          self.p_rules: should be an argument to hypothesis' __init__
        Returns: a float, -inf <= x <= 0, log p(self.value)
        """
        n_operators = len(self.value.operators)+1
        n_variables = len(self.value.variables)+1
        total_arity = sum([op.arity+1 for op in self.value.operators])
        n_rules = len(self.value.rules)+1
        p_rules = 0.0
        for r in self.value.rules:
            p_rules += log_p(r.lhs, self.value.operators |
                             self.value.variables)
            rhs_signature = set(self.value.operators) | r.lhs.variables()
            p_rules += log_p(r.rhs, rhs_signature)
        return (geom.logpmf(k=n_operators, p=self.p_operators) +
                geom.logpmf(k=total_arity, p=self.p_arity) +
                geom.logpmf(k=n_variables, p=self.p_variables) +
                geom.logpmf(k=n_rules, p=self.p_rules) +
                p_rules) / self.prior_temperature

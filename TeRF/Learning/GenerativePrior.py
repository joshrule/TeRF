import LOTlib.Miscellaneous as Misc
import scipy.stats as ss


class GenerativePrior(object):

    @Misc.attrmem('prior')
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
        signature = trs.signature.operators
        n_operators = len(signature)+1
        total_arity = sum(op.arity+1 for op in signature)
        n_rules = trs.num_rules()+1
        p_rules = sum(signature.log_p_rule(rule, invent=True)
                      for rule in trs)
        return (ss.geom.logpmf(k=n_operators, p=self.p_operators) +
                ss.geom.logpmf(k=total_arity, p=self.p_arity) +
                ss.geom.logpmf(k=n_rules,     p=self.p_rules) +
                p_rules) / self.prior_temperature

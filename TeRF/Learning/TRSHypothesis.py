from LOTlib.Hypotheses.Hypothesis import Hypothesis

from TeRF.Learning.GenerativePrior import GenerativePrior
from TeRF.Learning.Likelihood import Likelihood
from TeRF.Learning.TestProposer import TestProposer


class TRSHypothesis(GenerativePrior, Likelihood, TestProposer, Hypothesis):
    """
    A Hypothesis in the space of Term Rewriting Systems (TRS)

    The args below are TRSHypothesis specific. The Hypothesis baseclass also
    has: value, prior_temperature, likelihood_temperature, & display.

    Args:
      data: a list of Rules to explain
      p_partial: partial credit for an incorrect answer
      p_operators: probability of adding a new operator
      p_arity: probability of increasing the arity of an operator
      p_rules: probability of adding a new rule
      p_r: probability of regenerating any given subtree
      proposers: the components of the mixture
      weights: the weights of the mixture components
    """
    def __init__(self, temperature=1.0, **kwargs):
        self.temperature = temperature
        self.__dict__.update(kwargs)
        super(TRSHypothesis, self).__init__(**kwargs)

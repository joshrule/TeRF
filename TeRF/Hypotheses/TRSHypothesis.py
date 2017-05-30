from copy import deepcopy
from LOTlib.Hypotheses.Hypothesis import Hypothesis
from LOTlib.Inference.Samplers.StandardSample import standard_sample

from TeRF.Hypotheses.TRSGenerativePrior import TRSGenerativePrior
from TeRF.Hypotheses.TRSLikelihood import TRSLikelihood
from TeRF.Hypotheses.TRSUnrestrictedProposer import TRSUnrestrictedProposer
from TeRF.parser import load_source
from TeRF.TRS import RR, gensym
from TeRF.Utilities import sample_term, rewrite


class TRSHypothesis(TRSGenerativePrior, TRSLikelihood, TRSUnrestrictedProposer,
                    Hypothesis):
    """A Hypothesis in the space of Term Rewriting Systems (TRS)

    The args below are TRSHypothesis specific. The Hypothesis baseclass also
    has: value, prior_temperature, likelihood_temperature, & display.

    Args:
      p_observe: rate of observation (in timesteps)
      p_similar: rate of noisiness in evaluation (in timesteps)
      p_operators: probability of adding a new operator
      p_arity: probability of increasing the arity of an operator
      p_variables: probability of adding a new variable
      p_rules: probability of adding a new rule
      p_r: probability of regenerating any given subtree
      proposers: the components of the mixture
      weights: the weights of the mixture components

    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        super(TRSHypothesis, self).__init__(**kwargs)


def test(n, filename):
    trs, _ = load_source(filename)

    print 'Ground Truth:\n{:d}\n{}\n'.format(id(trs), trs)

    def make_data():
        data = set()
        while len(data) < 10:
            lhs = sample_term(trs.operators)
            rhs = rewrite(trs, lhs, steps=10)
            if lhs != rhs:
                data.add(RR(lhs, rhs))
        while len(data) < 100:
            lhs = sample_term(trs.operators)
            rhs = rewrite(trs, lhs, steps=10)
            data.add(RR(lhs, rhs))
        return data

    def make_hypothesis(data):
        hyp_trs = deepcopy(trs)
        hyp_trs.rules = []
        # hyp_trs.rules = list(data)
        return TRSHypothesis(value=hyp_trs,
                             gensym=gensym,
                             p_observe=0.1,
                             p_similar=0.99,
                             p_operators=0.5,
                             p_arity=0.9,
                             p_variables=0.5,
                             p_rules=0.5,
                             p_r=0.1)

    return standard_sample(make_hypothesis, make_data,
                           save_top=None, show_skip=999, trace=False, N=10,
                           steps=n)

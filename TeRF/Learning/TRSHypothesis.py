from copy import deepcopy
from LOTlib.Hypotheses.Hypothesis import Hypothesis
from LOTlib.Inference.Samplers.StandardSample import standard_sample
from numpy.random import choice
from scipy.stats import geom

from TeRF.Learning.GenerativePrior import GenerativePrior
from TeRF.Learning.Likelihood import Likelihood
from TeRF.Learning.TestProposer import TestProposer
from TeRF.Language.parser import load_source
from TeRF.Types import R, Sig


class TRSHypothesis(GenerativePrior, Likelihood, TestProposer, Hypothesis):
    """
    A Hypothesis in the space of Term Rewriting Systems (TRS)

    The args below are TRSHypothesis specific. The Hypothesis baseclass also
    has: value, prior_temperature, likelihood_temperature, & display.

    Args:
      p_observe: rate of observation (in timesteps)
      p_similar: rate of noisiness in evaluation (in timesteps)
      p_operators: probability of adding a new operator
      p_arity: probability of increasing the arity of an operator
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

    print '# Ground Truth:\n{}\n'.format(trs)

    def make_data():
        data = set()
        nChanged = 25
        nTotal = 50
        while len(data) < nTotal:
            lhs = Sig(trs.operators).sample_term()
            ws = [geom.pmf(k=x, p=0.1)/geom.cdf(k=10, p=.1)
                  for x in range(1, 11)]
            n_steps = choice(range(1, 11), p=ws)
            rhs = lhs.rewrite(trs, max_steps=n_steps)
            rule = R(lhs, [rhs])
            if len(data) < nChanged and lhs != rhs and rule not in trs.rules:
                data.add(rule)
            elif len(data) >= nChanged and rule not in trs.rules:
                data.add(rule)
        return data

    def make_hypothesis(data):
        hyp_trs = deepcopy(trs)
        hyp_trs.rules = list(data)
        return TRSHypothesis(value=hyp_trs,
                             privileged_ops=hyp_trs.operators,
                             p_observe=0.1,
                             p_similar=0.99,
                             p_operators=0.5,
                             p_arity=0.9,
                             p_rules=0.5,
                             p_r=0.3)

    hyps = standard_sample(make_hypothesis, make_data,
                           save_top=None, show_skip=99, trace=True, N=10,
                           steps=n, likelihood_temperature=1.0)

    print '\n\n# The best hypotheses of', n, 'samples:'
    for hyp in hyps.get_all(sorted=True):
        print hyp.prior, hyp.likelihood, hyp.posterior_score, hyp


if __name__ == '__main__':
    test(3200, 'library/simple_tree_manipulations/001.terf')

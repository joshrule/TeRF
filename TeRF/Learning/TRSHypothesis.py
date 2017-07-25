import copy
from LOTlib.Hypotheses.Hypothesis import Hypothesis
from LOTlib.Inference.Samplers.StandardSample import standard_sample
from numpy import exp
from numpy.random import choice
from scipy.misc import logsumexp

from TeRF.Learning.GenerativePrior import GenerativePrior
from TeRF.Learning.Likelihood import Likelihood
from TeRF.Learning.TestProposer import TestProposer
from TeRF.Language.parser import load_source
from TeRF.Types.TRS import TRS
from TeRF.Types.Rule import Rule
from TeRF.Types.Application import App


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


def fix_ps(log_ps):
    sum_ps = logsumexp(log_ps)
    return [exp(p-sum_ps) for p in log_ps]


def test(n, filename, start_string):
    trs, _ = load_source(filename)

    start = App(trs.signature.find(start_string), [])

    print '# Ground Truth:\n{}\n'.format(trs)

    def make_data_maker(nChanged=10, nTotal=20):
        def make_data():
            try:
                input = raw_input
            except NameError:
                pass

            data = TRS()
            temp = copy.deepcopy(trs)
            data.signature = copy.deepcopy(trs.signature)

            for i, rule in enumerate(list(temp.rules())):
                print '{:d}: {}'.format(i, rule)
                use_it = None
                while use_it not in ['y', '', 'n']:
                    use_it = input('Include this rule ([y]/n)? ')
                if use_it == 'n':
                    del temp[rule]

            print
            print 'Start symbol:', start.pretty_print()
            trace = start.rewrite(temp, max_steps=5, type='all', trace=True)
            states = trace.root.leaves(states=['normal'])
            terms = [s.term for s in states]
            log_ps = [s.log_p for s in states]
            ps = fix_ps(log_ps)

            print 'starting selection with {:d} rules'.format(data.num_rules())
            tries = 0
            while data.num_rules() < nTotal:
                tries += 1
                lhs = choice(terms, p=ps)  # ignoring ps to speed generation
                rhs = lhs.rewrite(trs, max_steps=5, type='one')
                rule = Rule(lhs, rhs)
                if (rule not in trs) and (((data.num_rules() < nChanged) and
                                           (lhs != rhs)) or
                                          data.num_rules() >= nChanged):
                    data[len(data)] = rule
            print 'tries:', tries
            return list(data.rules())
        return make_data

    def make_hypothesis(data):
        hyp_trs = TRS()
        for rule in data:
            for op in rule.operators:
                hyp_trs.signature.add(op)
            if rule.lhs not in rule.rhs:
                hyp_trs.add(rule)
        return TRSHypothesis(value=hyp_trs,
                             privileged_ops={s for s in hyp_trs.signature},
                             p_observe=0.1,
                             p_similar=0.99,
                             p_operators=0.5,
                             p_arity=0.9,
                             p_rules=0.5,
                             start=start,
                             p_r=0.3)

    hyps = standard_sample(make_hypothesis, make_data_maker(),
                           save_top=None, show_skip=49, trace=True, N=10,
                           steps=n)

    print '\n\n# The best hypotheses of', n, 'samples:'
    for hyp in hyps.get_all(sorted=True):
        print hyp.prior, hyp.likelihood, hyp.posterior_score, hyp


if __name__ == '__main__':
    # test(100, 'library/simple_tree_manipulations/001.terf', 'tree')
    test(3200, 'library/simple_tree_manipulations/001.terf', 'tree')

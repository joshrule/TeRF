import LOTlib
from LOTlib.TopN import TopN
from LOTlib.Miscellaneous import qq
from LOTlib import break_ctrlc
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.Inference.Samplers.ParallelTemperedMH import \
    ParallelTemperedMHSampler
from LOTlib.Inference.Samplers.AnnealedMH import AnnealedMHSampler


samplers = {
    'MH': MHSampler,
    'Annealed': AnnealedMHSampler,
    'Tempered': ParallelTemperedMHSampler
}


def test_sample(h0, data, show_skip=9, N=100, show=True, which_sampler='MH',
                **kwargs):
    """
    a custom interface for sampling TRSs

    METROPOLIS HASTINGS ARGUMENTS:
    - steps: how many steps to take total (Infinity)
    - proposer: custom function for generating proposals (None)
    - skip: throw out this many samples before yielding a new sample (0)
    - temperature: how much weight on prob. of accepting proposals?
    - trace: print stuff as we sample (False)
    - shortcut_likelihood: exit likelihood comp. if value is too low (True)

    ADDITIONAL PARALLEL TEMPERING ARGUMENTS:
    - steps: how many steps to take total, across all temperatures (Infinity)
    - temperatures: a list of temperatures to use ([1.0, 1.05, 1.15, 1.2])
    - within_steps: how many steps inside a chain before switching chains (100)
    - swaps: how many swaps to propose during each swap proposal (2)
    - yield_only_t0: provide samples only from lowest temperature (False)
    - print_swapstats: report when proposing swaps (False)
    - whichtemperature: which temperature to temper ('likelihood_temperature')

    ADDITIONAL SIMULATED ANNEALING ARGUMENTS:
    what : {'chain', 'hypothesis'}
        what is being annealed, the chain or the hypothesis
    schedule : LOTlib.Inference.Samplers.AnnealingSchedule, optional
        the schedule according to which the temperature is annealed
        (default: constant schedule of 1.0)
    """
    if LOTlib.SIG_INTERRUPTED:
        return TopN()

    best_hypotheses = TopN(N=N)

    sampler = samplers[which_sampler](h0, data, **kwargs)

    for i, h in enumerate(break_ctrlc(sampler)):

        best_hypotheses.add(h)

        if show and i % (show_skip+1) == 0:
            print '{}: {:.3f} = {:.3f} + {:.3f}\n{}'.format(
                i, h.posterior_score, h.prior, h.likelihood, qq(h))

    return best_hypotheses

import LOTlib.Hypotheses.Hypothesis as H
import TeRF.Learning.LOTSimplePrior as p
import TeRF.Learning.LOTLikelihood as L
import TeRF.Learning.LOTProposer as P


class LOTHypothesis(p.LOTSimplePrior, L.LOTLikelihood, P.LOTProposer,
                    H.Hypothesis):
    """
    hypothesis over Languages of Thought (LOTs)

    The args below are LOTHypothesis-specific. The Hypothesis baseclass also
    has: value, prior_temperature, likelihood_temperature, & display.

    Parameters
    ----------
    templates: list of TeRF.Types.Rule
        rule templates to be used during sampling
    temperature: float
        the temperature of the hypothesis itself
    data: list of TeRF.Types.Rule
        a list of rules to explain
    p_partial: float (0-1)
        how much partial credit for an incorrect answer
    p_rule:
        probability (*not* log probability) of adding a new rule
    proposers: list of proposer function pairs
        the components of the proposer mixture
    weights: list of floats
        the weights of the mixture components
    """
    def __init__(self, templates=None, temperature=0.0, **kwargs):
        self.templates = templates
        self.temperature = temperature
        self.__dict__.update(kwargs)
        super(LOTHypothesis, self).__init__(templates=templates, **kwargs)

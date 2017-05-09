from LOTlib.Hypotheses.Hypothesis import Hypothesis
from math import log


class TRSHypothesis(Hypothesis):
    """A Hypothesis in the space of Term Rewriting Systems (TRS)"""

    def __init__(self, value=None, **kwargs):
        """Create a TRSHypothesis

        :param value: the initial TRS
        :param normal_form_weight: how much to favor normal forms (0.0 to 1.0)
        """
        Hypothesis.__init__(self, None, **kwargs)

        if 'normal_form_weight' in kwargs:
            self.normal_form_weight = kwargs['normal_form_weight']
        else:
            self.normal_form_weight = 0.5

        if 'p_var' in kwargs:
            self.p_var = kwargs['p_var']
        else:
            self.p_var = 0.1
            
        self.set_value(value)

    def set_value(self, value):
        Hypothesis.set_value(self, value)

    def compute_prior(self):
        """the log prior of the hypothesis

        The prior reflects the /size/ of the TRS: # symbols in the signature +
        # rules + # nodes in each rule (lhs + rhs)
        """
        return -len(self.value) / self.prior_temperature

    def compute_single_likelihood(self, datum):
        """the log likelihood of the hypothesis for a single datum

        The likelihood has two parts: a generative part and a consistency part.
        Basically, it asks how likely the lhs of the datum is under S and how
        likely that lhs is to evaluate to the rhs under R.
        
        Ignores self.likelihood_temperature as compute_likelihood manages it.
        """
        n_steps, evals_to, nf = self.value.evals_to(datum.lhs, datum.rhs)
        return (log_p(self.value.signature, datum.lhs, self.p_var) +
                (log(self.normal_form_weight) if nf else
                 log(1.0-self.normal_form_weight)) +
                -(n_steps if evals_to else float('Inf')))
    
    def propose(self, **kwargs):
        """How do we move from one TRSHypothesis to another?
        
        This function provides a basic proposal mechanism which searches over
        all possible TRSs but can easily be changed to search over different
        classes of TRSs.
        """
        # MixtureProposer(proposers=[], proposer_weights=[])
        pass


def log_p(sig, term, p_var):
    """the log probability of generating a term from a signature"""
    n_vars = len(term.list_variables())
    n_symbols = len(sig) + n_vars
    return -(n_symbols * len(term)) - (p_var*n_vars)

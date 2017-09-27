import heapq as hq
import itertools as I
import numpy as np
import scipy as sp
import scipy.misc as sm
import numpy.random as random
import TeRF.Miscellaneous as M


class TraceComplete(Exception):
    pass


class Trace(object):
    """
    An evaluation trace for a TRS term

    Parameters
    ----------
    trs : TeRF.Types.TRS
        a term rewriting system (TRS)
    term : TeRF.Types.Term
        a term to be rewritten according to `trs`
    type : {'all', 'one'}
        pursue all possible rewrities or just one?
    p_observe : float
        how likely are you to observe non-normal forms (optional, 0.0)
    strategy : {'eager', 'normal', 'none'}
        how do you want to perform rewrites?
    max_steps : int
        how many total evaluation steps should the trace contain? Takes
        precedence over other exploration strategies. If None, treat as np.inf
        (optional, None)
    max_depth : int
        how long should the longest evaluation chain be? Takes precedence over
        `min_p` and `total_p`. If None, treat as np.inf (optional, None)
    total_p: float
        the upper bound on the amount of mass that will be explored. Takes
        precedence over `min_p`. If None, treat as 1.0 (optional, None)
    min_p : float
        the lower bound of the mass a leaf must contain to be expanded. If
        None, treat as 0.0 (optional, None)
    """
    def __init__(self, trs, term, type='all', p_observe=0.0, strategy='eager',
                 max_steps=None, max_depth=None, min_p=None, total_p=None):
        root = TraceState(term, 0)
        self.unobserved = []
        hq.heappush(self.unobserved, root)
        self.steps = 0
        self.root = root
        self.trs = trs
        self.type = type
        self.p_observe = p_observe
        self.strategy = strategy
        if max_steps is not None:
            self.max_steps = max_steps
        elif max_depth is not None:
            self.max_depth = max_depth
        elif total_p is not None:
            self.total_p = total_p
        elif min_p is not None:
            self.min_p = min_p

    @property
    def depth(self):
        return max([s.depth for s in self.root.leaves()])

    @property
    def size(self):
        return 1 + self.root.number_of_descendents

    @property
    def mass(self):
        # the mass is 1 - the mass in unobserved leaves
        x = [s.log_p for s in self.root.leaves(states=['start', 'unobserved'])]
        return (1.0 - np.exp(sm.logsumexp(x)))

    def sample(self):
        outcomes = self.root.leaves()
        ps = [np.exp(o.log_p) for o in outcomes]
        return random.choice(outcomes, p=ps)

    def run(self):
        while True:
            try:
                self.step()
            except TraceComplete:
                return self

    def report(self, trace=False, states=None):
        if trace:
            return self
        outcomes = self.root.leaves()
        outcomes = self.root.leaves(states=states)
        if self.type == 'one':
            if len(outcomes) == 1:
                return outcomes[0].term
            print [o.term for o in outcomes]
            print [o.state for o in outcomes]
            raise ValueError('Trace.report: more than one outcome (' +
                             str(len(outcomes)) + ')!')
        return [o.term for o in outcomes]

    def rewrite(self, trace=False, states=None):
        return self.run().report(trace, states=states)

    def step(self):
        if (hasattr(self, 'max_steps') and self.steps >= self.max_steps) or \
           (hasattr(self, 'total_p') and self.mass >= self.total_p):
            raise TraceComplete('Trace.step: no more steps can be taken')

        try:
            state = hq.heappop(self.unobserved)
        except IndexError:
            raise TraceComplete('Trace.step: no further steps can be taken')

        # in case we care about the number of steps taken
        self.steps += 1

        if (hasattr(self, 'max_depth') and state.depth <= self.max_depth) or \
           (hasattr(self, 'min_p') and np.exp(state.log_p) > self.min_p) or \
           hasattr(self, 'max_steps') or hasattr(self, 'total_p'):
            rewrites = state.term.single_rewrite(self.trs, type='all',
                                                 strategy=self.strategy)

            if rewrites is None or rewrites == []:
                state.state = 'normal'
            else:
                for term in rewrites:
                    new_p = M.logNof(rewrites) + state.log_p + \
                            M.log(1-self.p_observe)
                    unobserved = TraceState(term,
                                            state.depth+1,
                                            log_p=new_p,
                                            parent=state,
                                            state='unobserved')
                    hq.heappush(self.unobserved, unobserved)
                    state.children.append(unobserved)
                state.log_p += M.log(self.p_observe)

            # if only exploring a single path, kill the other paths
            if self.type == 'one' and state.children != []:
                self.unobserved = []
                chosen_one = random.choice(state.children)
                if chosen_one.state == 'unobserved':
                    hq.heappush(self.unobserved, chosen_one)
                state.children = [chosen_one]

    def rewrites_to(self, term):
        # NOTE: we only use tree equality and don't consider tree edit distance
        self.run()
        terms = [l.log_p for l in self.root.leaves()
                 if l.term.unify(term, type='alpha')]
        return sp.misc.logsumexp(terms) if terms else -np.inf


class TraceState(object):
    """A single state in a Trace"""
    def __init__(self, term, depth, log_p=0.0, parent=None, state='start'):
        self.term = term
        self.depth = depth
        self.log_p = log_p
        self.parent = parent
        self.state = state
        self.children = []

    def leaves(self, states=None):
        if self.children != []:
            return list(I.chain(*[c.leaves(states=states)
                                  for c in self.children]))
        return [self] if states is None or self.state in states else []

    def __cmp__(self, other):
        return self.log_p < other.log_p

    @property
    def number_of_descendents(self):
        return len(self.children) + sum(c.number_of_descendents
                                        for c in self.children)

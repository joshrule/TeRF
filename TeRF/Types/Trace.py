from heapq import heappush, heappop
from itertools import chain
from numpy import exp
from numpy.random import choice

from TeRF.Miscellaneous import log, log1of


class TraceComplete(Exception):
    pass


class Trace(object):
    """An evaluation trace for a TRS term"""
    def __init__(self, trs, term, type='all', p_observe=0.2,
                 max_steps=10, min_p=1e-6):
        root = TraceState(term, 0)
        self.unobserved = []
        heappush(self.unobserved, root)
        self.root = root
        self.trs = trs
        self.type = type
        self.p_observe = p_observe
        self.max_steps = max_steps
        self.min_p = min_p

    @property
    def steps(self):
        return max([s.step for s in self.root.leaves()])

    def sample(self):
        outcomes = self.root.leaves()
        ps = [exp(o.log_p) for o in outcomes]
        return choice(outcomes, p=ps)

    def run(self):
        while True:
            try:
                self.step()
            except TraceComplete:
                return self

    def report(self, trace=False):
        if trace:
            return self
        outcomes = self.root.leaves()
        if self.type == 'one':
            if len(outcomes) == 1:
                return outcomes[0].term
            print [o.term for o in outcomes]
            print [o.state for o in outcomes]
            raise ValueError('Trace.report: more than one outcome (' +
                             str(len(outcomes)) + ')!')
        return [o.term for o in self.root.leaves()]

    def rewrite(self, trace=False):
        return self.run().report(trace)

    def step(self):
        try:
            state = heappop(self.unobserved)
        except IndexError:
            raise TraceComplete('step: no further steps can be taken')

        if state.log_p < log(self.min_p) or self.steps > self.max_steps:
            raise TraceComplete('step: no further steps can be taken')

        rewrites = state.term.single_rewrite(self.trs, type='all')

        if rewrites == [state.term] or rewrites is None:
            state.state = 'normal'
        else:
            for term in rewrites:
                unobserved = TraceState(term,
                                        state.step+1,
                                        log_p=(log1of(rewrites) + state.log_p),
                                        parent=state,
                                        state='unobserved')
                heappush(self.unobserved, unobserved)
                state.children.append(unobserved)

        # if only exploring a single path, kill the other paths
        if self.type == 'one' and state.children != []:
            self.unobserved = []
            chosen_one = choice(state.children)
            if chosen_one.state == 'unobserved':
                heappush(self.unobserved, chosen_one)
            state.children = [chosen_one]

    def rewrites_to(self, term):
        # NOTE: we only use tree equality and don't consider tree edit distance
        self.run()
        return sum(l.log_p + int(l.state != 'normal')*log(self.p_observe)
                   for l in self.root.leaves() if l.term == term)


class TraceState(object):
    """A single state in a Trace"""
    def __init__(self, term, step, log_p=0.0, parent=None, state='start'):
        self.term = term
        self.step = step
        self.log_p = log_p
        self.parent = parent
        self.state = state
        self.children = []

    def leaves(self):
        if self.children != []:
            return list(chain(*[c.leaves() for c in self.children]))
        return [self]

    def __cmp__(self, other):
        return self.log_p < other.log_p

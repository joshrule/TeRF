import itertools as ittl
import numpy as np
import TeRF.Types.Application as A
import TeRF.Types.Variable as V


def distribute_lengths(length, arity):
    true_length = length - arity
    distribution = [np.ones(arity)]
    for _ in xrange(true_length):
        new_distribution = set()
        for arr in set(ittl.permutations([1] + list(ittl.repeat(0, arity-1)))):
            for item in distribution:
                new_distribution.add(tuple(np.array(item, dtype=int) +
                                           np.array(arr, dtype=int)))
        distribution = list(new_distribution)
    return [list(x) for x in distribution]


class TermEnumerator(object):
    def __init__(self, signature):
        self.signature = signature

    def enumerate(self, max_nodes=3, invent=True):
        return list(ittl.chain(*(self.enumerate_at(d, invent)
                                 for d in xrange(1, max_nodes+1))))

    def enumerate_at(self, depth, invent):
        if not (self.signature.terminals or invent):
            raise ValueError('enumerate_at: no terminals!')
        sig = self.signature.copy()

        # base case: return constants & variables
        if depth == 1:
            if invent:
                sig.add(V.Var())
            return [(A.App(s, []) if hasattr(s, 'arity') else s)
                    for s in sig.terminals]

        # recursive case: choose an appropriate head and make some gifts
        heads = sig.copy()
        for s in self:
            if getattr(s, 'arity', 0) > depth-1 or getattr(s, 'arity', 0) < 1:
                heads.discard(s)

        terms = []
        for head in heads.operators:
            distribution = distribute_lengths(depth-1, head.arity)
            for d in distribution:
                bodies = sig.bodies_with_distribution(d, invent)
                terms += [A.App(head, list(body)) for body in bodies]
        return terms

    def bodies_with_distribution(self, distribution, invent):
        subterms = self.enumerate_at(distribution[0], invent)
        bodies = [[st] for st in subterms]
        for nodes in distribution[1:]:
            new_bodies = []
            for body in bodies:
                body_sig = self.signature.copy()
                for a in {a for b in body for a in b.atoms}:
                    body_sig.add(a)
                subterms = TermEnumerator(body_sig).enumerate_at(nodes, invent)
                body_extensions = [body + [st] for st in subterms]
                new_bodies += body_extensions
            bodies = new_bodies
        return bodies

from itertools import repeat
from numpy.random import choice
from zss import distance as zss_distance


class Term(object):
    """Terms are trees built of variables or operators applied to terms"""
    def pretty_print(self, verbose=0):
        raise NotImplementedError

    def substitute(self, sub):
        raise NotImplementedError

    def unify(self, t, env=None, type='simple'):
        raise NotImplementedError

    def rewrite(self, trs, max_steps=1, type='one', trace=False):
        if type == 'one':  # hack! trace only works for rewrite_one
            return self.rewrite_one(trs, max_steps, trace)
        return self.rewrite_all(trs, max_steps)

    def rewrite_all(self, trs, max_steps=1):
        terms = [self]
        for _ in repeat(None, max_steps):
            terms_out = []
            for t in terms:
                outcomes = t.single_rewrite(trs, type)
                terms_out += [t] if outcomes is None else outcomes
            if terms_out == terms:
                break
            terms = terms_out
        return terms

    def rewrite_one(self, trs, max_steps=1, trace=False):
        the_trace = [self]
        term = self
        for _ in repeat(None, max_steps):
            term_out = term.single_rewrite(trs)
            if term_out is None or term == term_out:
                break
            term = term_out
            the_trace.append(term)
        return (the_trace if trace else term)

    def single_rewrite(self, trs, type='one'):
        """
        Perform a single rewrite of term using the TRS trs.

        Args:
          trs: a TRS a la TRS.py
          term: a Term a la TRS.py, the term to be rewritten
          type: how many possible rewrites to return either 'one' or 'all'
        Returns:
          None if no rewrite is possible, otherwise a single rewrite if type is
            'one' and all possible single rewrites if type is 'all'
        """
        for rule in trs.rules:
            sub = rule.lhs.unify(self, type='match')
            if sub is not None:
                if type == 'one':
                    return choice(rule.rhs).substitute(sub)
                return [rhs.substitute(sub) for rhs in rule.rhs]

        return self.single_rewrite_helper(trs, type)

    def distance(self, other):
        def get_cs(t):
            return t.body if hasattr(t, 'body') else []

        def insert_c(t):
            return 1

        def remove_c(t):
            return 1

        def update_c(t1, t2):
            return 0 if t1 == t2 else 1

        return zss_distance(self, other, get_cs, insert_c, remove_c, update_c)

    def differences(self, other):
        """all mismatching pairs of corresponding subtrees in self & other"""
        return [] if self == other else self.difference_helper(other)

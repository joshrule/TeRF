import collections


class SignatureError(Exception):
    pass


class Signature(collections.MutableSet):
    def __init__(self, elements=None, parent=None):
        self.parent = parent
        self._elements = set(([] if elements is None else elements))

    @property
    def variables(self):
        return Signature({v for v in self._elements
                          if not hasattr(v, 'arity')})

    @property
    def operators(self):
        return Signature({o for o in self._elements
                          if hasattr(o, 'arity')})

    @property
    def terminals(self):
        return {s for s in self._elements if s.terminal}

    def __contains__(self, item):
        return (item in self._elements)

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        for x in self._elements:
            yield x

    def __eq__(self, other):
        try:
            return self._elements == other._elements
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{' + ', '.join(str(s) for s in self._elements) + '}'

    def copy(self, parent=None):
        return Signature(self._elements,
                         parent=(parent if parent else None))

    def add(self, item):
        self._elements.add(item)

    def update(self, items):
        self._elements.update(items)

    def discard(self, item):
        self._elements.discard(item)
        if self.parent is not None:
            for rule in self.parent:
                if item in rule.variables or item in rule.operators:
                    del self.parent[rule]

    def replace_vars(self, new_vars):
        elements = set()
        for op in self.operators:
            elements.add(op)
        for var in new_vars:
            elements.add(var)
        self._elements = elements
        return self

    def find(self, name, arity=None):
        for s in self.operators:
            if s.name == name and (arity is None or s.arity == arity):
                return s

    def possible_roots(self, must_haves):
        if len(must_haves) == 0:
            return list(self)
        if len(must_haves) == 1:
            return [s for s in self
                    if s in must_haves or getattr(s, 'arity', 0) > 0]
        # technically not correct you could let S/1 be head if
        # must_haves = {S/1, 0/0}
        return [s for s in self if getattr(s, 'arity', 0) > 1]

    def get_counts(self, terms):
        """
        count how many times each operator appears in a list of terms

        Parameters
        ----------
        signature : TeRF.Types.Signature
            the signature from which we get our operators
        terms : list of TeRF.Types.Term
            the terms over which to count operators
        """
        counts = {op: 0 for op in self.operators}

        for term in terms:
            for t in term.subterms:
                try:
                    counts[t.head] += 1
                except KeyError:
                    if hasattr(t, 'arity'):
                        raise ValueError('get_counts: term is invalid ' +
                                         'under signature')
                    pass

        return counts


Sig = Signature

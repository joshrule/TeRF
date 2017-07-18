import collections as C
import copy

import TeRF.Types.Signature as S


class TRS(C.MutableMapping):
    def __init__(self):
        self.signature = S.Signature(parent=self)
        self._order = []
        self._rules = {}

    def __str__(self):
        return '[\n  Signature: ' + \
            ', '.join(str(s) for s in self.signature) + \
            '\n  Rules:\n    ' + \
            ',\n    '.join(str(rule) for rule in self) + '\n]'

    def __eq__(self, other):
        return self._order == other._order and \
            self._rules == other._rules and \
            self.signature == other.signature

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((frozenset(self.signature),
                     tuple(self._rules),
                     tuple(self._order)))

    def __setitem__(self, index, value):
        """
        Args:
          index: an integer, the order the rule should take. This would be used
            as a key in most mappings, but here it acts as an index, because
            the key comes from the value itself
          value: a Rule, the LHS is used as the key
        """
        if self.signature.operators >= value.operators:
            if value.lhs not in self:
                self._rules[value.lhs] = value
            else:
                self[value.lhs].add(value)
                self._order.remove(value.lhs)
            self._order.insert(index, value.lhs)
        else:
            raise ValueError('TRS.__setitem__: inconsistent signature')

    def __getitem__(self, key):
        # assume key is a rule -- not a common case, probably
        # does it make sense to return only part of the rule?
        try:
            rule = self._rules[key.lhs]
            if key in rule:
                env = rule.lhs.unify(key.lhs, type='alpha')
                return key.substitute(env)
        except (AttributeError, KeyError, ValueError):
            pass

        # assume key is a term
        try:
            return self._rules[key]
        except KeyError:
            pass

        # assume key is a number
        try:
            return self._rules[self._order[key]]
        except TypeError:
            raise KeyError

    def __delitem__(self, key):
        # assume it's a rule
        try:
            self._rules[key.lhs].discard(key)
            if len(self._rules[key.lhs]) == 0:
                self._order.remove(key.lhs)
                del self._rules[key.lhs]
            return
        except AttributeError:
            pass

        # assume it's a term
        try:
            self._order.remove(key)
            del self._rules[key]
            return
        except (ValueError, KeyError, TypeError):
            pass

        # assume it's a number
        del self._rules[self._order[key]]
        del self._order[key]

    def __iter__(self):
        order = copy.copy(self._order)
        for lhs in order:
                yield self._rules[lhs]

    def __len__(self):
        return sum(1 for _ in self)

    def rules(self):
        for lhs in self._order:
            for rule in self._rules[lhs]:
                yield rule

    def num_rules(self):
        return sum(1 for _ in self.rules())

    def index(self, value):
        return self._order.index(value)

    def clear(self):
        self.signature = S.Signature(parent=self)
        self._order = []
        self._rules = {}

    def add(self, rule):
        self[len(self)] = rule

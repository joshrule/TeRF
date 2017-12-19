import collections
import copy
import TeRF.Algorithms.Unify as u


class TRS(collections.MutableMapping):
    def __init__(self, rule_types, rules=None):
        self.rule_types = list(rule_types)
        self._order = []
        self._rules = {}
        if rules is not None:
            self.update(rules)

    def __delitem__(self, key):
        # assume it's a rule
        try:
            the_lhs = None
            for lhs in self._rules.keys():
                if u.alpha(lhs, key.lhs) is not None:
                    the_lhs = lhs
                    break
            self._rules[the_lhs].discard(key)
            if len(self._rules[the_lhs]) == 0:
                self._order.remove(the_lhs)
                del self._rules[the_lhs]
            return
        except AttributeError:
            pass

        # assume it's a term
        try:
            the_lhs = None
            for lhs in self._rules.keys():
                if u.alpha(lhs, key):
                    the_lhs = lhs
                    break
            self._order.remove(the_lhs)
            del self._rules[the_lhs]
            return
        except (ValueError, KeyError, TypeError):
            pass

        # assume it's a number
        del self._rules[self._order[key]]
        del self._order[key]

    def __eq__(self, other):
        return self._order == other._order and self._rules == other._rules

    def __getitem__(self, key):
        try:
            the_lhs = None
            for lhs in self._order:
                if u.alpha(lhs, key.lhs) is not None:
                    the_lhs = lhs
                    break
            if the_lhs is not None:
                rule = self._rules[the_lhs]
                for r in rule:
                    if key in r:
                        return r
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

    def __hash__(self):
        return hash((tuple(self._rules), tuple(self._order)))

    def __iter__(self):
        order = self._order[:]
        for lhs in order:
                yield self._rules[lhs]

    def __len__(self):
        return sum(1 for _ in self)

    def __ne__(self, other):
        return not self == other

    def __setitem__(self, index, value):
        """
        Args:
          index: an integer, the order the rule should take. This would be used
            as a key in most mappings, but here it acts as an index, because
            the key comes from the value itself
          value: a Rule, the LHS is used as the key
        """
        value = copy.deepcopy(value)
        the_lhs = None
        for lhs in self._rules.keys():
            if u.alpha(lhs, value.lhs) is not None:
                the_lhs = lhs
                break
        if the_lhs is None:
            self._rules[value.lhs] = value
            the_lhs = value.lhs
        else:
            self[the_lhs].add(value)
            self._order.remove(the_lhs)
        self._order.insert(index, the_lhs)

    def __repr__(self):
        string = 'TRS(rule_types={!r}, rules={!r})'
        return string.format(self.rule_types, [self._rules[lhs]
                                               for lhs in self._order])

    def __str__(self):
        return '\n'.join(str(rule) for rule in self)

    @property
    def operators(self):
        return {op for rule in self for op in rule.operators}

    @property
    def clauses(self):
        return [rule
                for lhs in self._order
                for rule in self._rules[lhs]]

    @property
    def size(self):
        return sum(s.size for s in self)

    def move(self, i1, i2):
        key = self._order[i1]
        del self._order[i1]
        self._order.insert(i2, key)

    def replace(self, r1, r2):
        try:
            rule = self[r1.lhs]
        except KeyError:
            raise ValueError('replace: rule to replace does not exist')
        rule.discard(r1)
        self.add(r2)
        if len(rule) == 0:
            del self[rule]
        return self

    def add(self, rule, idx=0):
        try:
            self[rule.lhs].add(rule)
        except KeyError:
            self[idx] = rule

    def update(self, rules):
        for rule in rules:
            self.add(rule)

    def index(self, value):
        return self._order.index(value)

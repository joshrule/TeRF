import collections
import copy
import itertools as it
import TeRF.Types.Signature as S


class TRS(collections.MutableMapping):
    def __init__(self):
        self.signature = S.Signature(parent=self)
        self._order = []
        self._rules = {}

    def __str__(self):
        return 'Signature: ' + \
            ', '.join(str(s) for s in self.signature) + \
            '\nRules:\n  ' + \
            ',\n  '.join(str(rule) for rule in self)

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
            print self.signature.operators
            print value.operators
            raise ValueError('TRS.__setitem__: inconsistent signature')

    def __getitem__(self, key):
        try:
            rule = self._rules[key.lhs]
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
        order = self._order[:]
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
        try:
            self[rule.lhs].add(rule)
        except KeyError:
            self[0] = rule

    def find_insertion(self, other):
        """if self == other + one more rule, return that rule, else None"""
        self2 = copy.deepcopy(self)
        new_rules = {rule for rule in self2.rules() if rule not in other}
        if len(new_rules) == 1:
            rule = new_rules.pop()
            del self2[rule]
            if self2 == other:
                return rule
        return None

    def find_difference(self, other):
        s_rules = {rule for rule in self.rules() if rule not in other}
        o_rules = {rule for rule in other.rules() if rule not in self}
        if len(s_rules) == len(o_rules) == 1:
            return s_rules.pop(), o_rules.pop()
        return (None, None)

    def find_move(self, other):
        if len(self) == len(other):
            s_rules = {rule for rule in self.rules() if rule not in other}
            o_rules = {rule for rule in other.rules() if rule not in self}
            if s_rules == o_rules == set():
                moves = [(self._order.index(other._order[i]), i)
                         for i, key in enumerate(self._order)
                         if i != self._order.index(other._order[i]) and
                         i < self._order.index(other._order[i])]
                if len(moves) == 1:
                    return moves[0]
        return (None, None)

    def swap(self, r1, r2):
        try:
            stored_rule = self[r1.lhs]
        except KeyError:
            raise ValueError('TRS.swap: rule to swap out does not exist')
        stored_rule.discard(r1)
        self.add(r2)
        if len(stored_rule) == 0:
            del self[stored_rule]
        return self

    def move(self, i1, i2):
        key = self._order[i1]
        del self._order[i1]
        self._order.insert(i2 + (0 if i2 < i1 else 1), key)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write('signature ')
            f.write(' '.join(str(op) for op in self.signature) + ';\n')
            f.write(';\n'.join([str(rule) for rule in self])+';\n')

    def unifies(self, other, env=None, type='alpha'):
        if self.signature == other.signature and \
           self.num_rules() == other.num_rules():
            for r_self, r_other in it.izip(self, other):
                if r_self.unify(r_other, env=env, type=type) is None:
                    return False
            return True
        return False

    def features(self):
        feats = {}
        feats['n_rules'] = self.num_rules()
        feats['n_nodes'] = sum(len(r.lhs) + len(r.rhs0) for r in self.rules())
        feats['n_lhss'] = len(self)
        feats['mean_rule_len'] = (float(feats['n_nodes']) /
                                  float(feats['n_rules']))
        feats['max_rule_len'] = max(len(r.lhs) + len(r.rhs0)
                                    for r in self.rules())
        feats['n_vars'] = sum(1 for r in self.rules()
                              for t in it.chain(r.lhs.subterms, r.rhs0.subterms)
                              if not hasattr(t, 'body'))
        feats['%_vars'] = float(feats['n_vars']) / float(feats['n_nodes'])
        feats['n_nondet_rules'] = sum(1 for r in self if len(r) > 1)
        feats['n_nondets'] = sum(len(r) for r in self if len(r) > 1)
        feats['%_nondets'] = float(feats['n_nondet_rules']) / \
                             float(feats['n_lhss'])
        return feats

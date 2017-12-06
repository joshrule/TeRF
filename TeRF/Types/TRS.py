import collections
import copy
import TeRF.Types.Application as A
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as R


class TRS(collections.MutableMapping):
    def __init__(self, rules=None, start=None, locked=True):
        if start is None:
            self.start = A.App(Op.Operator('START', 0), [])
        elif start.head.arity != 0:
            raise ValueError('start symbol has non-zero arity')
        else:
            self.start = start

        self._order = []
        self._rules = {}

        if rules is not None:
            self.update(rules)

    def __iter__(self):
        order = self._order[:]
        for lhs in order:
                yield self._rules[lhs]

    def __len__(self):
        return sum(1 for _ in self)

    def __delitem__(self, key):
        # assume it's a rule
        try:
            the_lhs = None
            for lhs in self._rules.keys():
                if lhs.unify(key.lhs, type='alpha') is not None:
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
                if lhs.unify(key, type='alpha'):
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

    def __getitem__(self, key):
        try:
            the_lhs = None
            for lhs in self._order:
                if lhs.unify(key.lhs, type='alpha') is not None:
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
            if lhs.unify(value.lhs, type='alpha') is not None:
                the_lhs = lhs
                break
        if the_lhs is None:
            self._rules[value.lhs] = value
            the_lhs = value.lhs
        else:
            self[the_lhs].add(value)
            self._order.remove(the_lhs)
        self._order.insert(index, the_lhs)

    def update(self, rules):
        for rule in rules:
            self.add(rule)

    def add(self, rule):
        try:
            self[rule.lhs].add(rule)
        except KeyError:
            self[0] = rule

    @property
    def operators(self):
        return {op for rule in self for op in rule.operators}

    def __str__(self):
        return '\n'.join(str(rule) for rule in self)

    @property
    def clauses(self):
        return [rule
                for lhs in self._order
                for rule in self._rules[lhs]]

    # def log_p(self, p_rule):
    #     p_n_rules = stats.geom.logpmf(len(self.clauses)+1, p=p_rule)
    #     p_rules = sum(rule.log_p for rule in self)
    #     return p_n_rules + p_rules

    def __eq__(self, other):
        return self._order == other._order and \
            self._rules == other._rules and \
            self.start == other.start and \
            self.scope == other.scope

    def __ne__(self, other):
        return not self == other

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

    def __hash__(self):
        return hash((tuple(self._rules),
                     tuple(self._order),
                     self.start))


if __name__ == '__main__':
    import TeRF.Types.Variable as V

    def f(x, xs=None):
        if xs is None:
            xs = []
        return A.App(x, xs)

    # test Grammar
    s = Op.Operator('S', 0)
    K = Op.Operator('K', 0)
    i = Op.Operator('I', 0)
    x = V.Variable('x')
    y = V.Variable('y')
    z = V.Variable('z')
    a = Op.Operator('.', 2)

    lhs_s = f(a, [f(a, [f(a, [f(s), x]), y]), z])
    rhs_s = f(a, [f(a, [x, z]), f(a, [y, z])])
    lhs_k = f(a, [f(a, [f(K), x]), y])
    rhs_k = x

    rule_s = R.Rule(lhs_s, rhs_s)
    rule_k = R.Rule(lhs_k, rhs_k)

    g = TRS(rules={rule_s, rule_k})

    print '\nGrammar:\n', g

    # test rewriting
    term = f(a, [f(a, [f(K), f(a, [f(a, [f(K), f(i)]), f(s)])]), f(s)])

    print '\nterm:\n', term.to_string()
    print '\nrewrite:'
    print '\n'.join(t.to_string() for t in term.rewrite(g)), '\n'


#    @property
#    def size(self):
#        return sum(r.size for r in self)
#
#    def index(self, value):
#        return self._order.index(value)
#
#    def clear(self):
#        self._order = []
#        self._rules = {}
#
#    def unifies(self, other, env=None, type='alpha'):
#        if len(self) == len(other):
#            for r_self, r_other in ittl.izip_longest(self, other):
#                if r_self.unify(r_other, env=env, type=type) is None:
#                    return False
#            return True
#        return False
#
#    def prettify(self, change=None):
#        self.rename_operators(change)
#        for rule in self:
#            rule.rename_variables()
#
#    def rename_operators(self, change=None):
#        if change is not None:
#            to_rename = [op for op in self.operators if op in change]
#            new_names = np.random.choice(P.pseudowords,
#                                         size=len(to_rename),
#                                         replace=False)
#            for op, name in ittl.izip(to_rename, new_names):
#                for rule in self.rules():
#                    for term in rule.lhs.subterms:
#                        if term.head == op:
#                            term.head.name = name
#                    for term in rule.rhs0.subterms:
#                        if term.head == op:
#                            term.head.name = name
#                op.name = name

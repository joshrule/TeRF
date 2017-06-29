class TRS(object):
    def __init__(self):
        self.operators = set()
        self.rules = []

    def add_op(self, operator):
        self.operators.add(operator)
        return self

    def del_op(self, operator):
        try:
            self.operators.remove(operator)
            self.rules = [r for r in self.rules if operator not in r.operators]
        except:
            pass
        return self

    def add_rule(self, rule, index=None):
        for r in self.rules:
            sub = r.lhs.unify(rule.lhs, type='alpha')
            if sub is not None:
                r.rhs += [rhs.substitute(sub) for rhs in rule.rhs]
                break
        else:
            index = len(self.rules) if index is None else index
            self.rules.insert(index, rule)
        return self

    def del_rule(self, item):
        try:  # treat as a rule
            for r in self.rules:
                sub = r.lhs.unify(item.lhs, type='alpha')
                if sub is not None:
                    spec = [rhs.substitute(sub) for rhs in item.rhs]
                    r.rhs = [r for r in r.rhs if r not in spec]
                if r.rhs == []:
                    self.rules.remove(r)
                break
        except (ValueError, AttributeError):  # could be an index
            try:
                del self.rules[item]
            except (TypeError, IndexError):  # not an index
                pass
        return self

    def __str__(self):
        return '[\n  Operators: ' + \
            ', '.join(o.name + '/' + str(o.arity) for o in self.operators) + \
            '\n  Rules:\n    ' + \
            ',\n    '.join(str(rule) for rule in self.rules) + '\n]'

    def __len__(self):
        return sum(len(r) for r in self.rules + [self.rules, self.operators])

    def __eq__(self, other):
        return self.rules == other.rules and self.operators == other.operators

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((tuple(self.rules), frozenset(self.operators)))

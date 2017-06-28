from TeRF.Rewrite import unify, substitute


class TRSError(Exception):
    pass


class RewriteRule(object):
    def __init__(self, lhs, rhss):
        if hasattr(lhs, 'head'):
            self.lhs = lhs
            self.variables = lhs.variables
            self.operators = lhs.operators
            self.rhs = []
            for rhs in rhss:
                if self.lhs.variables >= rhs.variables:
                    self.rhs.append(rhs)
                    self.operators |= rhs.operators
                else:
                    raise TRSError('Rule rhs invents variables')
        else:
            raise TRSError('t1 much be an application')

    def __str__(self):
        lhs_str = self.lhs.pretty_print()
        start = lhs_str + ' = '
        padding = '\n' + ' '*(len(lhs_str)+1) + '| '
        finish = padding.join(rhs.pretty_print() for rhs in self.rhs)
        return start + finish

    def __repr__(self):
        return 'RewriteRule({}, {})'.format(self.lhs, self.rhs)

    def __len__(self):
        return len(self.lhs) + sum(len(rhs) for rhs in self.rhs)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))


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
            self.rules = [r for r in self.rules
                          if operator not in r.operators]
        except:
            pass
        return self

    def add_rule(self, rule, index=0):
        for r in self.rules:
            sub = unify(r.lhs, rule.lhs, type='alpha')
            if sub is not None:
                r.rhs = [substitute(rhs, sub) for rhs in rule.rhs] + r.rhs
                break
        else:
            self.rules.insert(index, rule)
        return self

    def del_rule(self, item):
        try:  # treat as a rule
            for r in self.rules:
                sub = unify(r.lhs, item.lhs, type='alpha')
                if sub is not None:
                    spec = [substitute(rhs, sub) for rhs in item.rhs]
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
        return (len(self.operators) +
                len(self.rules) +
                sum(len(r) for r in self.rules))

    def __eq__(self, other):
        return self.rules == other.rules and self.operators == other.operators

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((tuple(self.rules), frozenset(self.operators)))


RR = RewriteRule

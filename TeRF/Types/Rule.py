class Rule(object):
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
                    raise ValueError('Rule rhs invents variables')
        else:
            raise ValueError('t1 must be an application')

    def __str__(self):
        lhs = self.lhs.pretty_print()
        rhs = ' | '.join(rhs.pretty_print() for rhs in self.rhs)
        return lhs + ' = ' + rhs

    def __repr__(self):
        return 'Rule({}, {})'.format(self.lhs, self.rhs)

    def __len__(self):
        return len(self.lhs) + sum(len(rhs) for rhs in self.rhs)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))


R = Rule

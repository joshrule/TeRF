import TeRF.Types.Atom as A


class Operator(A.Atom):
    """an Atom with arity"""

    def __init__(self, name=None, arity=0):
        self.arity = arity
        super(Operator, self).__init__(name=name,
                                       terminal=(arity == 0))

    def __str__(self):
        return '{}/{:d}'.format(self.name, self.arity)

    def __repr__(self):
        return 'Operator(\'{}\', {:d})'.format(self.name, self.arity)

    def __eq__(self, other):
        try:
            return self.arity == other.arity and self.name == other.name
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = hash((self.arity, self.name))
        return self._hash

    def pretty_print(self):
        return self.name


Op = Operator

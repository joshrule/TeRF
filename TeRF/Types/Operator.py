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

    def pretty_print(self):
        return self.name


Op = Operator

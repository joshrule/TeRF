import TeRF.Types.Atom as A


class Operator(A.Atom):
    """
    a TeRF.Types.Atom with arity

    Parameters
    ----------
    arity : int
        the arity of the operator
    """
    def __init__(self, name=None, arity=0, **kwargs):
        self.arity = arity
        super(Operator, self).__init__(name=name,
                                       terminal=(arity == 0),
                                       **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        string = 'Operator(name=\'{}\', arity={:d})'
        return string.format(self.name, self.arity)

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

    def fullname(self):
        return '{}/{:d}'.format(self.name, self.arity)


Op = Operator

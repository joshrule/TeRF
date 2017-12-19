import TeRF.Types.Atom as A


class Operator(A.Atom):
    """
    a TeRF.Types.Atom with arity and a name

    Parameters
    ----------
    name : str
        the user-readable name of the operator
    arity : int
        the arity of the operator
    """
    def __init__(self, name, arity=0, **kwargs):
        self.arity = arity
        self.name = name
        super(Operator, self).__init__(**kwargs)

    def __eq__(self, other):
        try:
            return self.arity == other.arity and \
                self.name == other.name
        except AttributeError:
            return False

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = hash((self.name, self.arity))
        return self._hash

    def __repr__(self):
        return 'Operator(name={!r}, arity={!r}, identity={!r})'.format(
            self.name, self.arity, self.identity)

    def __str__(self):
        return self.name


Op = Operator

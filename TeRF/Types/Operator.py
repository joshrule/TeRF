from TeRF.Types.Atom import Atom


class Operator(Atom):
    """a lone operator of fixed arity"""
    def __init__(self, name=None, arity=0):
        self.arity = arity
        super(Operator, self).__init__(name=name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return ('Operator(\'{}\', {:d})').format(self.name, self.arity)

    def fullname(self):
        return "{}/{:d}".format(self.name, self.arity)

    def is_atom(self):
        return self.arity == 0

    def __eq__(self, other):
        try:
            return (self.arity == other.arity and self.name == other.name)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.name, self.arity))


Op = Operator

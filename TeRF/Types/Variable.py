import TeRF.Types.Atom as Atom
import TeRF.Types.Term as Term


class Variable(Atom.Atom, Term.Term):
    """
    an unspecified term

    Parameters
    ----------
    name : string (default=None)
        The name of the variable
    """
    def __init__(self, name=None, **kwargs):
        super(Variable, self).__init__(head=self, **kwargs)
        self._cache = {}
        self.name = (name if name is not None else 'v' + str(self.identity))

    def __hash__(self):
        try:
            return self._cache['hash']
        except KeyError:
            self._cache['hash'] = hash((self.name, self.identity))
        return self._cache['hash']

    def __repr__(self):
        return 'Variable(name={!r}, identity={})'.format(
            self.name, self.identity)

    def __str__(self):
        return self.name + '_'


Var = Variable

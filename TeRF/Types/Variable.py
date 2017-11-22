import copy
import TeRF.Types.Atom as A
import TeRF.Types.Term as T


class Variable(T.Term, A.Atom):
    """an unspecified term"""
    def __init__(self, name=None, **kwargs):
        super(Variable, self).__init__(name=name,
                                       terminal=True,
                                       head=self,
                                       **kwargs)

    def __str__(self):
        return self.name + '_'

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == 'identity':
                setattr(result, k, v)
            elif k in ['_atoms', '_places', '_variables', '_operators']:
                pass
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __eq__(self, other):
        try:
            return self.identity == other.identity
        except AttributeError:
            return False

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = hash(self.identity)
        return self._hash

    def __len__(self):
        return 1

    def __ne__(self, other):
        return not self == other

    def atoms(self):
        try:
            return self._atoms
        except AttributeError:
            self._atoms = {self}
            return self._atoms

    def variables(self):
        try:
            return self._variables
        except AttributeError:
            self._variables = {self}
            return self._variables

    def operators(self):
        return set()

    @property
    def subterms(self):
        yield self

    def places(self):
        return []

    def place(self, place):
        if list(place) != []:
            raise ValueError('place: non-empty place')
        return self

    def replace(self, place, term):
        if list(place) == []:
            return term
        else:
            raise ValueError('replace: non-empty place')

    def to_string(self, verbose=0):
        return str(self)

    def substitute(self, env):
        try:
            return env[self]
        except KeyError:
            return self

    def unify(self, t, env=None, type='simple'):
        # see wikipedia.org/wiki/Unification_(computer_science)
        env = {} if env is None else env

        if self == t:
            return env
        if (type is not 'alpha' or not hasattr(t, 'body')) and\
           self not in t.variables():
            if self not in env:
                for var in env:
                    env[var] = env[var].substitute({self: t})
                env[self] = t
                return env
            if env[self] == t:
                return env
        return None

    def single_rewrite(self, g, type='one', strategy='eager'):
        return None


Var = Variable

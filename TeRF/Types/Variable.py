import TeRF.Types.Atom as A
import TeRF.Types.Term as T


class Variable(A.Atom, T.Term):
    """an unspecified term"""
    def __init__(self, name=None, **kwargs):
        super(Variable, self).__init__(name=name, terminal=True,
                                       head=self, **kwargs)

    def __str__(self):
        return self.name + '_'

    def __len__(self):
        return 1

    @property
    def atoms(self):
        yield self

    @property
    def subterms(self):
        yield self

    def pretty_print(self, verbose=0):
        return str(self)

    def substitute(self, env):
        try:
            return env[self]
        except KeyError:
            return self

    def unify(self, t, env=None, type='simple'):
        # see wikipedia.org/wiki/Unification_(computer_science)
        env = {} if env is None else env

        if self is t:
            return env
        if (type is not 'alpha' or not hasattr(t, 'body')) and\
           self not in t.variables:
            if self not in env:
                for var in env:
                    env[var] = env[var].substitute({self: t})
                env[self] = t
                return env
            if env[self] == t:
                return env
        return None

    def single_rewrite(self, trs, type):
        return None

    def differences(self, other, top=True):
        return [] if (self == other or not top) else [(self, other)]


Var = Variable

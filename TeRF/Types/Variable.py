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
            raise ValueError('Variable.substitute: not part of environment!')

    def unify(self, t, env=None, type='simple'):
        env = {} if env is None else env

        if self is t:
            if self not in env:
                env[self] = self
            return env
        if self in env:
            return env[self].unify(t, env, type)
        if t in env:
            return self.unify(env[t], env, type)
        if type is not 'alpha' or not hasattr(t, 'body'):
            env[self] = t
            return env
        if type is 'simple':
            return t.unify(self, env, type)
        return None

    def single_rewrite(self, trs, type):
        return None


Var = Variable

#    def difference_helper(self, other):
#        return [(self, other)]

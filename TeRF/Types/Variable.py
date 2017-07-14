import TeRF.Types.Atom as A
import TeRF.Types.Term as T
import TeRF.Types.Signature as S


class Variable(A.Atom, T.Term):
    """an unspecified term"""
    def __init__(self, name=None):
        super(Variable, self).__init__(name=name, terminal=True,
                                       head=self, signature=S.Signature())
        self.signature.add(self)  # need to wait until __hash__ is defied

    def pretty_print(self, verbose=0):
        return ('' if self.name == str(id(self.identity)) else self.name) + '_'

    def substitute(self, env):
        try:
            return env[self]
        except KeyError:
            raise ValueError('Variable.substitute: not part of environment!')

    def unify(self, t, env=None, type='simple'):
        env = {} if env is None else env

        if self is t:
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

    def __str__(self):
        return self.name + '_'

    def __len__(self):
        return 1


Var = Variable

#    def difference_helper(self, other):
#        return [(self, other)]

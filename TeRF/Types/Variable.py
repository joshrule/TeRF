import TeRF.Types.Atom as A
import TeRF.Types.Term as T
import TeRF.Types.Signature as S


class Variable(T.Term, A.Atom):
    """an unspecified term"""
    def __init__(self, name=None):
        A.Atom.__init__(self, name=name, terminal=True)
        # we need to define __hash__ via Atom before creating a signature
        T.Term.__init__(self, head=self, signature=S.Signature([self]))

    def pretty_print(self, verbose=0):
        return ('' if self.name == str(id(self.identity)) else self.name) + '_'

    def substitute(self, sub):
        try:
            return sub[self]
        except KeyError:
            raise ValueError('substitute: Variable has no definition!')

    def unify(self, t, env=None, type='simple'):
        env = {} if env is None else env

        if self is t:
            return env
        if self in env:
            return env[self].unify(t, env, type)
        if t in env:
            return self.unify(env[t], env, type)
        if type is not 'alpha' or not hasattr(t, 'arity'):
            env[self] = t
            return env
        if type is 'simple':
            return t.unify_var(self, env, type)
        return None

    def single_rewrite(self, trs, type):
        return None

    def __str__(self):
        return self.name + '_'

    def __repr__(self):
        return 'Variable(\'{}\')'.format(self.name)

    def __hash__(self):
        return hash(self.identity)

    def __len__(self):
        return 1

#    def difference_helper(self, other):
#        return [(self, other)]


Var = Variable

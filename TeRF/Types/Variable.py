from TeRF.Types.Atom import Atom
from TeRF.Types.Term import Term


class Variable(Atom, Term):
    """an arbitrary term"""
    def __init__(self, name=None):
        super(Variable, self).__init__(name=name)
        self.variables = {self}
        self.operators = set()

    def pretty_print(self, verbose=0):
        return self.name + '_'

    def substitute(self, sub):
        try:
            return sub[self]
        except KeyError:
            raise ValueError('substitute: Variable has no definition!')

    def unify(self, t, env=None, type='simple'):
        env = {} if env is None else env

        if self == t:
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

    def single_rewrite_helper(self, trs, type):
        return None

    def head(self):
        return self

    def is_atom(self):
        return True

    def difference_helper(self, other):
        return [(self, other)]

    def __str__(self):
        return self.name + '_'

    def __repr__(self):
        return 'Variable(\'{}\')'.format(self.name)

    def __eq__(self, other):
        try:
            return (self.identity == other.identity and
                    not hasattr(other, 'arity'))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.identity)

    def __len__(self):
        return 1


Var = Variable

import TeRF.Types.Trace as T


class Term(object):
    """
    Variables or Applications of Operators to Terms

    Parameters
    ----------
    head : TeRF.Types.Atom
        the root of the term
    """
    def __init__(self, head, **kwargs):
        self.head = head
        self._types = {}
        super(Term, self).__init__(**kwargs)

    def operators(self):
        raise NotImplementedError

    def variables(self):
        raise NotImplementedError

    def atoms(self):
        raise NotImplementedError

    def subterms(self):
        raise NotImplementedError

    def places(self):
        raise NotImplementedError

    def to_string(self, verbose=0):
        raise NotImplementedError

    def substitute(self, env):
        raise NotImplementedError

    def unify(self, t, env=None, type='simple'):
        raise NotImplementedError

    def single_rewrite(self, trs, type='one', strategy='eager'):
        raise NotImplementedError

    def place(self, place):
        raise NotImplementedError

    def replace(self, place, term):
        raise NotImplementedError

    def rewrite(self, g, trace=False, states=None, **kwargs):
        return T.Trace(g, self, **kwargs).rewrite(trace, states=states)

    def rename_variables(self):
        for i, v in enumerate(self.variables()):
            v.name = 'v' + str(i)

    def log_p(self, typesystem, type):
        env = {v: typesystem.make_tv() for v in self.variables()}
        return typesystem.log_p_term(self, type, typesystem.make_env(env))

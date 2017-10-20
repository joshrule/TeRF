import abc
import TeRF.Types.Trace as T


class Term(object):
    """
    Variables or Applications of Operators to Terms

    Parameters
    ----------
    head : TeRF.Types.Atom
        the root of the term
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, head, **kwargs):
        self.head = head
        super(Term, self).__init__(**kwargs)

    @property
    def operators(self):
        return {o for o in self.atoms if hasattr(o, 'arity')}

    @property
    def variables(self):
        return {v for v in self.atoms if not hasattr(v, 'arity')}

    @abc.abstractproperty
    def atoms(self): raise NotImplementedError

    @abc.abstractproperty
    def subterms(self): raise NotImplementedError

    @abc.abstractmethod
    def to_string(self, verbose=0): raise NotImplementedError

    @abc.abstractmethod
    def substitute(self, env): raise NotImplementedError

    @abc.abstractmethod
    def unify(self, t, env=None, type='simple'): raise NotImplementedError

    @abc.abstractmethod
    def single_rewrite(self, trs, type='one'): raise NotImplementedError

    @abc.abstractmethod
    def differences(self, other, top=True): raise NotImplementedError

    def rewrite(self, trs, trace=False, states=None, **kwargs):
        return T.Trace(trs, self, **kwargs).rewrite(trace, states=states)

    def rename_variables(self):
        for i, v in enumerate(self.variables):
            v.name = 'v' + str(i)

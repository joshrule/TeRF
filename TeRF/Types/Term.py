import abc
import TeRF.Types.Trace as T


class Term(object):
    """trees built of Variables or Operators applied to Terms"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, head, **kwargs):
        self.head = head
        super(Term, self).__init__(**kwargs)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

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
    def pretty_print(self, verbose=0): raise NotImplementedError

    @abc.abstractmethod
    def substitute(self, env): raise NotImplementedError

    @abc.abstractmethod
    def unify(self, t, env=None, type='simple'): raise NotImplementedError

    @abc.abstractmethod
    def single_rewrite(self, trs, type='one'): raise NotImplementedError

    @abc.abstractmethod
    def differences(self, other, top=True): raise NotImplementedError

    def rewrite(self, trs, trace=False, **kwargs):
        return T.Trace(trs, self, **kwargs).rewrite(trace)

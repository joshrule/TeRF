import abc

import TeRF.Types.Trace as T


class Term(object):
    """trees built of Variables or Operators applied to Terms"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, head, signature, **kwargs):
        self.head = head
        self.signature = signature
        super(Term, self).__init__(**kwargs)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    @abc.abstractmethod
    def pretty_print(self, verbose=0): raise NotImplementedError

    @abc.abstractmethod
    def substitute(self, env): raise NotImplementedError

    @abc.abstractmethod
    def unify(self, t, env=None, type='simple'): raise NotImplementedError

    @abc.abstractmethod
    def single_rewrite(self, trs, type='one'): raise NotImplementedError

    def rewrite(self, trs, trace=False, **kwargs):
        return T.Trace(trs, self, **kwargs).rewrite(trace)

    # def differences(self, other):
    #     """all mismatching pairs of corresponding subtrees in self & other"""
    #     return [] if self == other else self.difference_helper(other)

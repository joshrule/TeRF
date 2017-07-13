import TeRF.Types.Trace as T


class Term(object):
    """trees built of Variables or Operators applied to Terms"""

    def __init__(self, head, signature, **kwargs):
        self.head = head
        self.signature = signature

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def pretty_print(self, verbose=0):
        raise NotImplementedError

    def substitute(self, env):
        raise NotImplementedError

    def unify(self, t, env=None, type='simple'):
        raise NotImplementedError

    def rewrite(self, trs, max_steps=1, type='one', trace=False, **kwargs):
        t = T.Trace(trs, self, type=type, max_steps=max_steps, **kwargs)
        return t.run().report(trace)

    def single_rewrite(self, trs, type='one'):
        """
        Perform a single rewrite of term using the TRS trs.

        Args:
          term: a Term a la TRS.py, the term to be rewritten
          trs: a TRS a la TRS.py
          type: how many possible rewrites to return either 'one' or 'all'
        Returns:
          None if no rewrite is possible, otherwise a single rewrite if type is
            'one' and all possible single rewrites if type is 'all'
        """
        raise NotImplementedError

    # def differences(self, other):
    #     """all mismatching pairs of corresponding subtrees in self & other"""
    #     return [] if self == other else self.difference_helper(other)

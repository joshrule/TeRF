"""
TRS.py - representations for Term Rewriting Systems

Written by: Joshua Rule <joshua.s.rule@gmail.com>
"""


class TRSError(Exception):
    pass


class Term():
    pass


class Operator(object):
    """a lone operator"""

    def __init__(self, name, arity):
        self.name = name
        self.arity = arity  # can ARS/TRS have Operators without fixed arity?

    def __str__(self):
        return "{}/{:d}".format(self.name, self.arity)

    def __repr__(self):
        return ('Operator(name={}, '
                'arity={:d})').format(self.name, self.arity)


class Signature(object):
    """a set of operators"""
    def __init__(self, items):
        self.sig = {}
        for item in items:
            self.add(item)

    def add(self, operator):
        try:
            name = '{}/{}'.format(operator.name, operator.arity)
        except AttributeError:
            raise TRSError('Tried to add a non-operator to a signature')
        else:
            self.sig[name] = operator

    def get(self, key):
        return self.sig[key]

    def remove(self, key):
        del self.sig[key]

    def update(self, other):
        try:
            self.sig.update(other.sig)
        except AttributeError:
            raise TRSError('Tried to update a Signature with a non-Signature')

    def __str__(self):
        return str(self.sig)

    def __repr__(self):
        return 'Signature(' + str(self.sig.values()) + ')'

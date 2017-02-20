"""
TRS.py - representations for Term Rewriting Systems

Written by: Joshua Rule <joshua.s.rule@gmail.com>
"""


class Atom(object):
    def __init__(self, index, alias=None):
        self.index = index
        self.alias = alias


class Term(object):
    def __init__(self, signature):
        self.signature = signature

    def vars(self):
        raise NotImplementedError

    def symbols(self):
        raise NotImplementedError


class Symbol(Atom):
    def __init__(self, index, alias=None, arity=0):
        Atom.__init__(self, index=index, alias=alias)
        self.arity = arity  # can ARS/TRS have Symbols without fixed arity?

    def __str__(self):
        return self.alias if self.alias else "S{:d}".format(self.index)

    def __repr__(self):
        return ('Symbol(index={:d}, '
                'alias=\'{}\', '
                'arity={:d})').format(self.index,
                                      self.alias,
                                      self.arity)


class Variable(Atom, Term):
    """a lone variable"""
    def __init__(self, signature, index, alias=None):
        Atom.__init__(self, index=index, alias=alias)
        Term.__init__(self, signature)

    def __str__(self):
        return self.alias if self.alias else "V{:d}".format(self.index)

    def __repr__(self):
        return "Variable(index={:d}, alias=\'{}\')".format(self.index,
                                                           self.alias)

    def vars(self):
        return set([self])

    def symbols(self):
        return set([])


class Application(Term):
    """a function symbol applied to terms"""
    def __init__(self, signature, head, body=[],):
        sym_head = isinstance(head, Symbol)
        arity_match = len(body) is head.arity
        all_terms = all([isinstance(t, Term) for t in body])
        sig_match = all([t.signature == signature for t in body])
        if sym_head:
            if arity_match:
                if all_terms:
                    if sig_match:
                        Term.__init__(self, signature)
                        self.head = head
                        self.body = body
                    else:
                        raise SignatureViolationError
                else:
                    raise TRSError('Subterms must be Terms')
            else:
                raise TRSError(('{} has arity {:d}'
                                'but given {:d} args').format(
                                    head, head.arity, len(body)))
        else:
            raise TRSError('The head of an application must be a Term')

    def __str__(self):
        if len(self.body) is 0:
            body = ''
        else:
            body = '(' + ', '.join([str(t) for t in self.body]) + ')'
        return str(self.head) + body

    def __repr__(self):
        return 'Application(head={}, body={})'.format(self.head, self.body)

    def vars(self):
        return set([]).union(*[t.vars() for t in self.body])

    def symbols(self):
        return set([self.head]).union(*[t.symbols() for t in self.body])


class RewriteRule(object):
    def __init__(self, signature, lhs, rhs):
        sigs_match = lhs.signature == rhs.signature == signature
        lhs_is_app = isinstance(lhs, Application)
        lhs_ge_rhs = all([v in lhs.vars() for v in rhs.vars()])
        if sigs_match:
            if lhs_is_app:
                if lhs_ge_rhs:
                    self.signature = signature
                    self.lhs = lhs
                    self.rhs = rhs
                else:
                    raise TRSError('RHS {} has variables \
                        not in LHS {}'.format(rhs, lhs))
            else:
                raise TRSError('LHS cannot be a variable')
        else:
            SignatureViolationError

    def symbols(self):
        return self.lhs.symbols().union(self.rhs.symbols())

    def vars(self):
        return self.lhs.vars().unoin(self.rhs.vars())

    def __str__(self):
        return str(self.lhs) + ' -> ' + str(self.rhs)


class TRS(object):
    def __init__(self, signature, rules):
        all_rules = all([isinstance(r, RewriteRule) for r in rules])
        sigs_match = all([r.signature == signature for r in rules])
        if all_rules:
            if sigs_match:
                self.signature = signature
                self.rules = rules
            else:
                raise SignatureViolationError
        else:
            raise TypeError('TRS needs RewriteRule evaluation rules')

    def __str__(self):
        return str([str(s) for s in self.signature]) + \
            '\n\n' + '\n'.join([str(r) for r in self.rules])


class TRSError(Exception):
    pass


class SignatureViolationError(TRSError):
    pass


if __name__ == "__main__":

    # make SK-logic

    s = Symbol(1, 'S', 0)
    k = Symbol(2, 'K', 0)
    app = Symbol(3, '.', 2)
    sig = set([s, k, app])

    a = Variable(sig, 1, 'a')
    b = Variable(sig, 2, 'b')
    c = Variable(sig, 3, 'c')

    def make(x, y):
        return Application(sig, app, [x, y])

    t1 = make(make(make(Application(sig, s, []), a), b), c)
    t2 = make(make(a, c), make(b, c))
    r1 = RewriteRule(sig, t1, t2)

    t3 = make(make(Application(sig, k, []), a), b)
    t4 = a
    r2 = RewriteRule(sig, t3, t4)

    sk = TRS(sig, set([r1, r2]))

    print sk

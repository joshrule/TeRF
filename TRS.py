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






if __name__ == "__main__":

    # make SK-logic

    sk = TRS().add_operator(0).add_operator(0).add_operator(2)

    s = sk.signature[0]
    k = sk.signature[1]
    a = sk.signature[2]

    x = sk.new_var()
    y = sk.new_var()
    z = sk.new_var()

    def make(x, y):
        return Application(sk.signature, a, [x, y])

    t1 = make(make(make(Application(sk.signature, s, []), x), y), z)
    t2 = make(make(x, z), make(y, z))
    
    t3 = make(make(Application(sk.signature, k, []), x), y)
    t4 = x

    sk = sk.add_rule(t1, t2)
    sk = sk.add_rule(t2, t4)
    print sk

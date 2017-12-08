import TeRF.Types.Term as Term


class Application(Term.Term):
    """
    a term applying an operator to arguments

    Parameters
    ----------
    head : TeRF.Type.Operator
        the operator being applied
    args : list of TeRF.Type.Term
        the arguments to which the head is applied
    """
    def __init__(self, head, args):
        if head.arity == len(args):
            self._cache = {}
            self.args = args
            super(Application, self).__init__(head=head)
        else:
            string = 'arity mismatch {} != {}'.format(head.arity, len(args))
            raise Term.TermError(string)

    def __eq__(self, other):
        try:
            return self.head == other.head and self.args == other.args
        except AttributeError:
            return False

    def __hash__(self):
        try:
            return self._cache['hash']
        except KeyError:
            self._cache['hash'] = hash((self.head, tuple(self.args)))
        return self._cache['hash']

    def __len__(self):
        return 1 + sum(len(arg) for arg in self.args)

    def __repr__(self):
        return 'Application(head={!r}, args={!r})'.format(self.head, self.args)

    def __str__(self):
        return '{}[{}]'.format(self.head, ', '.join(str(x) for x in self.args))


App = Application

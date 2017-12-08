import TeRF.Miscellaneous as misc


class TermError(Exception):
    pass


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
        super(Term, self).__init__()

    def __deepcopy__(self, memo):
        return misc.empty_cache_deepcopy(self, memo)

    def __eq__(self, other):
        try:
            return self.head == other.head
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.head,))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'Term(head={!r})'.format(self.head)

    def __len__(self):
        return 1

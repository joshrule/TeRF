import TeRF.Miscellaneous as misc


class Atom(object):
    """the smallest units in terms"""
    next_id = 0

    def __init__(self, identity=None, **kwargs):
        self.identity = Atom.next_id
        Atom.next_id += 1
        super(Atom, self).__init__(**kwargs)

    def __deepcopy__(self, memo):
        return misc.empty_cache_deepcopy(self, memo)

    def __eq__(self, other):
        try:
            return self.identity == other.identity
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.identity,))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'Atom(identity={!r})'.format(self.identity)

    def __str__(self):
        return 'atom_{!r}'.format(self.identity)

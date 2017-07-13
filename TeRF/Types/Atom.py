class Atom(object):
    """the smallest units in terms"""

    def __init__(self, terminal, name=None, **kwargs):
        self.terminal = terminal
        self.identity = object()
        self.name = str(id(self.identity)) if name is None else name

    def __eq__(self, other):
        try:
            return self.identity == other.identity
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.identity)

    def __copy__(self):
        # I'm immutable
        return self

    def __deepcopy__(self, memo):
        # I'm immutable
        return self

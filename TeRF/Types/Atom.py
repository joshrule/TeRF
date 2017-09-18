import abc


class Atom(object):
    """the smallest units in terms"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, terminal, name=None, **kwargs):
        self.terminal = terminal
        self.identity = object()
        self.name = str(id(self.identity)) if name is None else name
        super(Atom, self).__init__(**kwargs)

#    def __copy__(self):
#        # I'm immutable
#        return self
#
#    def __deepcopy__(self, memo):
#        # I'm immutable
#        return self

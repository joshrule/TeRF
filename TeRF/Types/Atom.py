import copy


class Atom(object):
    """
    the smallest units in terms

    Parameters
    ----------
    terminal : bool
        True if this atom is considered a terminal of the language, else False
    name : string (default: None)
        the name of the atom. If None, the name comes from the identity.
    """
    def __init__(self, terminal, name=None, **kwargs):
        self.terminal = terminal
        self.identity = object()
        self.name = str(id(self.identity)) if name is None else name
        super(Atom, self).__init__(**kwargs)

    def __deepcopy__(self, memo):
        """custom __deepcopy__ preserving identity attributes"""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == 'identity':
                setattr(result, k, v)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

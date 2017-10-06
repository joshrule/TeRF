import abc
import copy


class Atom(object):
    """the smallest units in terms"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, terminal, name=None, **kwargs):
        self.terminal = terminal
        self.identity = object()
        self.name = str(id(self.identity)) if name is None else name
        super(Atom, self).__init__(**kwargs)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == 'identity':
                setattr(result, k, v)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

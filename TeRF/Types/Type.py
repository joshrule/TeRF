class TypeError(Exception):
    pass


class Type(object):
    """
    Hindley-Milner Types
    """
    def __ne__(self, other):
        return not self == other

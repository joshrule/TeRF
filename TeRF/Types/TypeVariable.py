import TeRF.Types.Type as Type


class TypeVariable(Type.Type):
    """a definite but unspecified type"""
    next_id = 0

    def __init__(self):
        self.id = TypeVariable.next_id
        TypeVariable.next_id += 1

    def __eq__(self, other):
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.id,))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'TypeVariable(id={!r})'.format(self.id)

    def __str__(self):
        return 'v' + str(self.id)


TVar = TypeVariable

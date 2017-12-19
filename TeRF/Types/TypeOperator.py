import TeRF.Miscellaneous as misc
import TeRF.Types.Type as Type


class TypeOperator(Type.Type):
    """
    an application of some type to subtypes


    Technically, my type hierarchy is wrong. I don't separate monotypes and
    polytypes, so it's possible to apply TypeOperators to polytypes...

    head: string
        the name of the operator
    args: list of TeRF.Types.Type
        the arguments to which the head is applied
    """
    def __init__(self, head, args):
        self.head = head
        self.args = args

    def __eq__(self, other):
        try:
            return self.head == other.head and self.args == other.args
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.head, tuple(self.args)))

    def __repr__(self):
        return 'TypeOperator(head={!r}, args={!r})'.format(self.head,
                                                           self.args)

    def __str__(self):
        if self.head == '->' and len(self.args) == 2:
            return misc.iter2ListStr(self.args, l='(', r=')', sep=' -> ')
        return str(self.head) + misc.iter2ListStr(self.args, empty='')

    def __ne__(self, other):
        return not self == other



TOp = TypeOperator

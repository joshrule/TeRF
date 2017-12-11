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
        super(TypeOperator, self).__init__()

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
        return str(self.head) + misc.iter2ListStr(self.args, empty='')


TOp = TypeOperator


class Function(TypeOperator):
    def __init__(self, alpha_type, beta_type):
        super(Function, self).__init__('->', [alpha_type, beta_type])

    def __str__(self):
        return misc.iter2ListStr(self.args, l='(', r=')', sep=' -> ')


F = Function

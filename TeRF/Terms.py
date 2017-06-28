class TermError(Exception):
    pass


class Atom(object):
    pass


class Operator(Atom):
    """a lone operator of fixed arity"""
    def __init__(self, name=None, arity=0):
        self.id = object()
        self.name = name if name is not None else 'o' + str(id(self.id))
        self.arity = arity

    def __str__(self):
        return self.name

    def __repr__(self):
        return ('Operator(name=\'{}\', '
                'arity={:d})').format(self.name, self.arity)

    def fullname(self):
        return "{}/{:d}".format(self.name, self.arity)

    def __eq__(self, other):
        try:
            return (self.arity == other.arity and self.name == other.name)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.name, self.arity))


class Term(object):
    """Terms are trees built of variables or operators applied to terms"""
    def pretty_print(self, verbose=0):
        raise NotImplementedError


class Variable(Atom, Term):
    """an arbitrary term"""
    def __init__(self, name=None, **kwargs):
        self.identity = object()  # gensym!
        self.name = name if name else 'v' + str(id(self.identity))
        self.str = self.name + '_'
        self.variables = {self}
        self.operators = set()
        super(Variable, self).__init__(**kwargs)

    def pretty_print(self, verbose=0):
        return self.str

    def __str__(self):
        return self.str

    def __repr__(self):
        return 'Variable(\'{}\')'.format(self.name)

    def __eq__(self, other):
        try:
            return (self.identity == other.identity)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.identity)

    def __len__(self):
        return 1


class Application(Term):
    """a term applying an operator to arguments"""
    def __init__(self, head, body, **kwargs):
        try:
            if head.arity == len(body):
                self.head = head
                self.body = body
                self.name = str(self.head)
                self.str = '{}[{}]'.format(
                    self.head,
                    ', '.join(str(x) for x in self.body))
                self.variables = {variable for part in self.body
                                  for variable in part.variables}
                self.operators = {self.head} | \
                                 {operator for part in self.body
                                  for operator in part.operators}
            else:
                raise ValueError('Application: arity != head length')
        except AttributeError:
            raise TermError('Application: head of term must be an operator')
        super(Application, self).__init__(**kwargs)

    def pretty_print(self, verbose=0):
        if self.head == Operator('.', 2):
            if verbose == 0:
                return self.body[0].pretty_print(0) + \
                    ' ' + self.body[1].pretty_print(1)
            elif verbose == 1:
                return '(' + self.body[0].pretty_print(0) + \
                    ' ' + self.body[1].pretty_print(1) + ')'
            else:
                return '(' + self.body[0].pretty_print(2) + \
                    ' ' + self.body[1].pretty_print(2) + ')'
        elif self.body:
            return str(self.head) + '[' + \
                ' '.join([b.pretty_print(1) for b in self.body]) + ']'
        else:
            return str(self.head)

    def __str__(self):
        return self.str

    def __repr__(self):
        return 'Application({},{})'.format(self.head, self.body)

    def __len__(self):
        return 1 + sum(len(t) for t in self.body)

    def __eq__(self, other):
        try:
            return self.head == other.head and self.body == other.body
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.head,) + tuple(self.body))


App = Application
Var = Variable
Op = Operator

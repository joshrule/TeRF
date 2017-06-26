class TRSError(Exception):
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
            raise TRSError('Application: head of term must be an operator')
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


class RewriteRule(object):
    def __init__(self, t1, t2):
        if hasattr(t1, 'head'):
            if t1.variables >= t2.variables:
                self.lhs = t1
                self.rhs = t2
                self.variables = t1.variables | t2.variables
                self.operators = t1.operators | t2.operators
            else:
                raise TRSError('Rule rhs invents variables')
        else:
            raise TRSError('t1 cannot be a variable')

    def __str__(self):
        return self.lhs.pretty_print() + ' = ' + self.rhs.pretty_print()

    def __repr__(self):
        return 'RewriteRule({}, {})'.format(self.lhs, self.rhs)

    def __len__(self):
        return len(self.lhs) + len(self.rhs)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, self.rhs))


class TRS(object):
    def __init__(self):
        self.operators = set()
        self.rules = []

    def add_op(self, operator):
        self.operators.add(operator)
        return self

    def del_op(self, operator):
        try:
            self.operators.remove(operator)
            self.rules = [r for r in self.rules
                          if operator not in r.operators]
        except:
            pass
        return self

    def add_rule(self, rule, index=None):
        try:
            self.rules.insert(index, rule)
        except TypeError:
            self.rules += [rule]
        return self

    def del_rule(self, item):
        try:  # treat as a rule
            self.rules.remove(item)
        except (ValueError, AttributeError):  # could be an index
            try:
                del self.rules[item]
            except TypeError:  # not an index
                pass
            except IndexError:  # index is too high or too low
                pass
        return self

    def __str__(self):
        return '[\n  Operators: ' + \
            ', '.join(o.name + '/' + str(o.arity) for o in self.operators) + \
            '\n  Rules:\n    ' + \
            ',\n    '.join(str(rule) for rule in self.rules) + '\n]'

    def __len__(self):
        return (len(self.operators) +
                len(self.rules) +
                sum(len(r) for r in self.rules))

    def __eq__(self, other):
        return self.rules == other.rules and self.operators == other.operators

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((tuple(self.rules), frozenset(self.operators)))


App = Application
Var = Variable
Op = Operator
RR = RewriteRule

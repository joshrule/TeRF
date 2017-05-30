from itertools import chain, imap

counter = 0

def gensym():
    global counter
    counter += 1
    return '#g_' + str(counter)


class TRSError(Exception):
    pass


class Atom(object):
    pass


class Operator(Atom):
    """a lone operator of fixed arity"""

    def __init__(self, name, arity):
        self.name = name
        self.arity = arity  # can ARS/TRS have Operators without fixed arity?

    def __str__(self):
        return self.name

    def __repr__(self):
        return ('Operator(name=\'{}\', '
                'arity={:d})').format(self.name, self.arity)

    def fullname(self):
        return "{}/{:d}".format(self.name, self.arity)

    def __eq__(self, other):
        try:
            return (self.arity is other.arity and self.name is other.name)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.name, self.arity))


class Term(object):
    """Terms are trees built of variables or operators applied to terms"""
    def variables(self):
        raise NotImplementedError

    def operators(self):
        raise NotImplementedError

    def pretty_print(self, verbose=0):
        raise NotImplementedError


class Variable(Atom, Term):
    """an arbitrary term"""
    def __init__(self, name=None, identity=None, **kwargs):
        self.name = name if name else gensym()
        self.identity = (identity if identity else
                         (gensym() if name else self.name))
        self.str = self.name + '_'
        super(Variable, self).__init__(**kwargs)

    def variables(self):
        return {self}

    def operators(self):
        return set()

    def pretty_print(self, verbose=0):
        return self.str

    def __str__(self):
        return self.str

    def __repr__(self):
        return 'Variable(\'{}\', \'{}\')'.format(self.name, self.identity)

    def __eq__(self, other):
        try:
            return (self.identity is other.identity)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.identity)

    def __len__(self):
        return 1

    def __iter__(self):
        yield self


class Application(Term):
    """a term applying an operator to arguments"""
    def __init__(self, head, body, **kwargs):
        try:
            if head.arity == len(body):
                self.head = head
                self.body = body
                self.str = '{}[{}]'.format(
                    self.head,
                    ', '.join(str(x) for x in self.body))
            else:
                raise ValueError('Application: arity != head length')
        except AttributeError:
            raise TRSError('Application: head of term must be an operator')
        super(Application, self).__init__(**kwargs)

    def variables(self):
        return {variable for part in self.body
                for variable in part.variables()}

    def operators(self):
        return {self.head} | \
               {operator for part in self.body
                for operator in part.operators()}

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
        return 1 + sum([len(st) for st in self.body])

    def __iter__(self):
        yield self
        for operand in chain(*imap(iter, self.body)):
            yield operand

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
        if t1.operators():
            if t1.variables() >= t2.variables():
                self.lhs = t1
                self.rhs = t2
            else:
                raise TRSError('Rule rhs invents variables')
        else:
            raise TRSError('t1 cannot be a variable')

    def variables(self):
        return self.lhs.variables() | self.rhs.variables()

    def operators(self):
        return self.lhs.operators() | self.rhs.operators()

    def __str__(self):
        return self.lhs.pretty_print() + ' = ' + self.rhs.pretty_print()

    def __repr__(self):
        return 'RewriteRule({}, {})'.format(self.lhs, self.rhs)

    def __len__(self):
        return len(self.lhs) + len(self.rhs)

    def __neq__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, self.rhs))


class TRS(object):
    def __init__(self):
        self.operators = set()
        self.variables = set()
        self.rules = []

    def add_op(self, operator):
        self.operators.add(operator)
        return self

    def del_op(self, operator):
        try:
            self.operators.remove(operator)
            self.rules = [r for r in self.rules
                          if operator not in r.operators()]
        except:
            pass
        return self

    def add_rule(self, rule, index=1000000):
        # hack to use 1e6...
        self.rules.insert(index, rule)
        return self

    def del_rule(self, item):
        try:  # treat as a rule
            self.rules.remove(item)
        except ValueError:  # could be an index
            try:
                del self.rules[item]
            except TypeError:  # not an index
                pass
            except IndexError:  # index is too high
                pass
        return self

    def add_var(self, variable):
        self.variables.add(variable)
        return self

    def del_var(self, item):
        try:  # to delete the variable itself and any rules using it
            self.variables.remove(item)
            self.rules = [r for r in self.rules if item not in r.variables()]
        except:
            pass
        return self

    def __str__(self):
        #     return '[' + str(self.operators) + ',\n ' + \
        #         str(self.variables) + ',\n [' + \
        #         ',\n  '.join([str(rule) for rule in self.rules]) + ']]'
        return '[\n  Operators: ' + \
            ', '.join(o.name + '/' + str(o.arity)
                      for o in self.operators) + \
            '\n  Variables: ' + \
            ', '.join(v.name for v in self.variables) + \
            '\n  Rules:\n    ' + \
            ',\n    '.join(str(rule) for rule in self.rules) + '\n]'

    def __len__(self):
        return (len(self.operators) +
                len(self.variables) +
                len(self.rules) +
                sum([len(r) for r in self.rules]))

    def __eq__(self, other):
        return self.rules == other.rules and \
            self.variables == other.variables and \
            self.operators == other.operators

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((tuple(self.rules),
                     frozenset(self.variables),
                     frozenset(self.operators)))


App = Application
Var = Variable
Op = Operator
RR = RewriteRule

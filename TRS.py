"""
TRS.py - representations for Term Rewriting Systems

Written by: Joshua Rule <joshua.s.rule@gmail.com>
"""

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
        return ('Operator(name={}, '
                'arity={:d})').format(self.name, self.arity)

    def fullname(self):
        return "{}/{:d}".format(self.name, self.arity)

    def __eq__(self, other):
        return self.name == other.name and self.arity == other.arity

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name + '/' + str(self.arity))


class Term(object):
    """Terms are trees built of variables or operators applied to terms"""
    def __init__(self, **kwargs):
        self.variables = self.list_variables()
        self.operators = self.list_operators()
    
    def list_variables(self):
        raise NotImplementedError

    def list_operators(self):
        raise NotImplementedError

    def pretty_print(self, verbose=0):
        raise NotImplementedError


class Variable(Atom, Term):
    """an arbitrary term"""
    def __init__(self, name=None, identity=None, **kwargs):
        self.name = name if name else gensym()
        self.identity = (identity if identity else
                         (gensym() if name else self.name))
        super(Variable, self).__init__(**kwargs)

    def list_variables(self):
        return {self}

    def list_operators(self):
        return set()

    def pretty_print(self, verbose=0):
        return str(self)

    def __str__(self):
        return self.name + '_'

    def __repr__(self):
        return 'Variable({}, {})'.format(self.name, self.identity)

    def __eq__(self, other):
        try:
            equal = self.name == other.name and self.identity == other.identity
        except AttributeError:
            return False
        else:
            return equal

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.name + self.identity)

    def __len__(self):
        return

    def __iter__(self):
        yield self


class Application(Term):
    """a term applying an operator to arguments"""
    def __init__(self, head, body, **kwargs):
        try:
            if head.arity == len(body):
                self.head = head
                self.body = body
        except AttributeError:
            raise TRSError('head of term is a variable')
        super(Application, self).__init__(**kwargs)

    def list_variables(self):
        return {variable for part in self.body for variable in part.variables}

    def list_operators(self):
        return {self.head} | \
               {operator for part in self.body for operator in part.operators}

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
        if self.body:
            return '{}[{}]'.format(self.head,
                                   ' '.join([str(arg) for arg in self.body]))
        else:
            return str(self.head)

    def __repr__(self):
        return 'Application({},{})'.format(self.head, self.body)

    def __len__(self):
        return 1 + sum([len(st) for st in self.body])

    def __iter__(self):
        yield self
        for operand in chain(*imap(iter, self.body)):
            yield operand


class RewriteRule(object):
    def __init__(self, t1, t2):
        if t1.operators:
            if t1.variables >= t2.variables:
                self.lhs = t1
                self.rhs = t2
                self.variables = self.list_variables()
                self.operators = self.list_operators()
            else:
                raise TRSError('Rule rhs invents variables')
        else:
            raise TRSError('t1 cannot be a variable')

    def list_variables(self):
        return self.lhs.list_variables() | self.rhs.list_variables()

    def list_operators(self):
        return self.lhs.list_operators() | self.rhs.list_operators()

    def __str__(self):
        return self.lhs.pretty_print() + ' = ' + self.rhs.pretty_print()

    def __repr__(self):
        return 'RewriteRule({}, {})'.format(self.lhs, self.rhs)

    def __len__(self):
        return len(self.lhs) + len(self.rhs)


class TRS(object):
    def __init__(self):
        self.signature = set()
        self.rules = []

    def add_operator(self, operator):
        if isinstance(operator, Operator):
            self.signature.add(operator)
        else:
            raise TRSError('Tried to add a non-operator to a signature')

    def del_operator(self, name, arity):
        try:
            op = Operator(name, arity)
            self.signature.remove(op)
            self.rules = [r for r in self.rules if op not in r.operators]
        except:
            pass

    def add_rule(self, rule):
        self.rules.append(rule)

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

    def add_variable(self, name=None):
        self.signature.add(Variable(name=name))

    def del_variable(self, item):
        try:  # to delete the variable itself and any rules using it
            self.signature.remove(item)
            self.rules = [r for r in self.rules if item not in r.variables]
        except:
            pass

    def __str__(self):
        return '[' + str(self.signature.keys()) + ',\n [' + \
            ',\n  '.join([str(rule) for rule in self.rules]) + ']]'

    def __len__(self):
        return (len(self.signature) +
                len(self.rules) +
                sum([len(r) for r in self.rules]))


App = Application
Var = Variable
Op = Operator

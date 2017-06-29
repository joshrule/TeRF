from itertools import izip, chain

from TeRF.Types.Term import Term
from TeRF.Types.Operator import Op


class ApplicationError(Exception):
    pass


class Application(Term):
    """a term applying an operator to arguments"""
    def __init__(self, head, body, **kwargs):
        try:
            if head.arity == len(body):
                self.head = head
                self.body = body
                self.name = str(self.head)  # for tree printing
                self.variables = {variable for part in self.body
                                  for variable in part.variables}
                self.operators = {self.head} | \
                                 {operator for part in self.body
                                  for operator in part.operators}
            else:
                raise ValueError('Application: arity != head length')
        except AttributeError:
            raise ApplicationError('head of term must be an operator')
        super(Application, self).__init__(**kwargs)

    def pretty_print(self, verbose=0):
        if self.head == Op('.', 2):
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

    def substitute(self, sub):
        return App(self.head, [t.substitute(sub) for t in self.body])

    def unify(self, t, env=None, type='simple'):
        env = {} if env is None else env

        try:
            if self.head == t.head:
                for (st1, st2) in izip(self.body, t.body):
                    env = st1.unify(st2, env, type)
                    if env is None:
                        break
                return env
        except AttributeError:  # treat t2 as variable
            if type is 'simple':
                return t.unify(self, env, type)
        return None

    def single_rewrite_helper(self, trs, type):
        for idx in xrange(len(self.body)):
            part = self.body[idx].single_rewrite(trs, type=type)
            if part is not None and type == 'one':
                return App(self.head,
                           self.body[:max(0, idx)] +
                           [part] +
                           self.body[max(1, idx+1):])
            if part is not None and type == 'all':
                return [App(self.head,
                            self.body[:max(0, idx)] +
                            [p] +
                            self.body[max(1, idx+1):])
                        for p in part]
        return None

    def head(self):
        return self.head

    def difference_helper(self, other):
        # TODO: What if heads have different arity?
        # TODO: What if other isn't an application?
        return [(self, other)] + \
            list(chain(*[st1.differences(st2)
                         for st1, st2 in izip(self.body, other.body)]))

    def __str__(self):
        return '{}[{}]'.format(self.head, ', '.join(str(x) for x in self.body))

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
        return not self == other

    def __hash__(self):
        return hash((self.head,) + tuple(self.body))


App = Application

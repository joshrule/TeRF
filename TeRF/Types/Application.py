import itertools as it
import numpy.random as random
import TeRF.Types.Term as T
import TeRF.Types.Variable as V


class Application(T.Term):
    """a term applying an operator to arguments"""

    def __init__(self, head, body):
        if head.arity == len(body):
            self.body = body
            super(Application, self).__init__(head=head)
        else:
            raise ValueError('Application: wrong number of arguments')

    def __eq__(self, other):
        try:
            return self.head == other.head and self.body == other.body
        except AttributeError:
            return False

    def __hash__(self):
        if not hasattr(self, '_hash'):
            self._hash = hash((self.head, tuple(hash(b) for b in self.body)))
        return self._hash

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return sum(1 for _ in self.subterms)

    def __repr__(self):
        return 'Application({}, {})'.format(repr(self.head), repr(self.body))

    def __str__(self):
        return '{}[{}]'.format(self.head, ', '.join(str(x) for x in self.body))

    def atoms(self):
        try:
            return self._atoms
        except AttributeError:
            self._atoms = ({self.head} |
                           {a for t in self.body for a in t.atoms()})
            return self._atoms

    def variables(self):
        try:
            return self._variables
        except AttributeError:
            atoms = self.atoms()
            self._variables = {v for v in atoms
                               if not hasattr(v, 'arity')}
            return self._variables

    def operators(self):
        try:
            return self._operators
        except AttributeError:
            atoms = self.atoms()
            self._operators = {o for o in atoms
                               if hasattr(o, 'arity')}
            return self._operators

    @property
    def subterms(self):
        yield self
        for term in self.body:
            for subterm in term.subterms:
                yield subterm

    def places(self):
        try:
            return self._places
        except AttributeError:
            self._places = [[]]
            for i, term in enumerate(self.body):
                for place in term.places():
                    self._places += [[i] + place]
            return self._places

    def place(self, place):
        if list(place) == []:
            return self
        try:
            return self.body[place[0]].place(place[1:])
        except IndexError:
            raise ValueError('place: invalid place')

    def replace(self, place, term):
        if list(place) == []:
            return term
        else:
            body = self.body[:]
            body[place[0]] = body[place[0]].replace(place[1:], term)
            return Application(self.head, body)

    def is_list(self):
        """
        this approach assumes we're using cons/0 to encode lists and must be
        changed if we decide to use a different encoding.
        """
        try:
            return (self.head.name == '.' and
                    self.head.arity == 2 and
                    self.body[0].head.name == '.' and
                    self.body[0].head.arity == 2 and
                    self.body[0].body[0].head.name == 'cons' and
                    self.body[0].body[0].head.arity == 0 and
                    self.body[1].is_list()) or \
                   (self.head.name == 'nil' and
                    self.head.arity == 0)
        except AttributeError:
            return False

    def is_number(self):
        """
        this approach assumes we're using S/1 to encode lists and must be
        changed if we decide to use a different encoding.
        """
        try:
            return (self.head.name == 'S' and
                    self.head.arity == 1 and
                    self.body[0].is_number()) or \
                   (self.head.name == '0' and
                    self.head.arity == 0)
        except AttributeError:
            return False

    def to_string(self, verbose=0):
        def list_terms(xs):
            try:
                return [xs.body[0].body[1]] + list_terms(xs.body[1])
            except IndexError:
                return []

        def print_list():
            """
            this approach assumes we're using cons to encode lists and will
            need to be changed if we decide to use a different encoding.
            """
            items = [t.to_string(verbose) for t in list_terms(self)]
            return '[' + ', '.join(items) + ']'

        def number_value(n):
            try:
                return 1 + number_value(n.body[0])
            except IndexError:
                return 0

        def print_number():
            return str(number_value(self))

        if self.is_list():
            return print_list()
        if self.is_number():
            return print_number()
        if self.head.name == '.' and self.head.arity == 2:
            if verbose == 0:
                return self.body[0].to_string(0) + \
                    ' ' + self.body[1].to_string(1)
            elif verbose == 1:
                return '(' + self.body[0].to_string(0) + \
                    ' ' + self.body[1].to_string(1) + ')'
            else:
                return '(' + self.body[0].to_string(2) + \
                    ' ' + self.body[1].to_string(2) + ')'
        body = '[{}]'.format(' '.join(b.to_string(1) for b in self.body)) \
               if self.body else ''
        return str(self.head) + body

    def substitute(self, sub):
        if sub is None:
            raise ValueError('Application.substitute: bad environment')
        return App(self.head, [t.substitute(sub) for t in self.body])

    def unify(self, t, env=None, type='simple'):
        # see wikipedia.org/wiki/Unification_(computer_science)
        env = {} if env is None else env

        try:
            if self.head == t.head:
                for (st1, st2) in it.izip(self.body, t.body):
                    env = st1.unify(st2, env, type)
                    if env is None:
                        break
                return env
        except AttributeError:  # treat t2 as variable
            if type is 'simple':
                return t.unify(self, env, type)
        return None

    def single_rewrite(self, g, type='one', strategy='eager'):

        def collect_options(g, start=None):
            start = g.start if start is None else start
            applications = list(g[start].rhs)
            variables = g.scope.find(start)
            new_var = [] if g.scope.locked else [V.Var()]
            options = applications + variables + new_var
            return options

        def rewrite_head():
            for rule in g:
                sub = rule.lhs.unify(self, type='match')
                if sub is not None:
                    options = collect_options(g, start=rule.lhs)
                    if type == 'one':
                        choice = random.choice(options)
                        if isinstance(choice, V.Var):
                            g.scope.scope[choice] = rule.lhs
                        return random.choice(options).substitute(sub)
                    for choice in options:
                        if isinstance(choice, V.Var) and choice not in g:
                            g.scope.scope[choice] = rule.lhs
                    return [o.substitute(sub) for o in options]

        def rewrite_body():
            for idx in xrange(len(self.body)):
                part = self.body[idx].single_rewrite(g, type, strategy)
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

        def rewrite_all():
            rewrites = []
            for idx in xrange(len(self.body)):
                parts = self.body[idx].single_rewrite(g, type, strategy)
                rewrites += [App(self.head,
                                 self.body[:max(0, idx)] +
                                 [p] +
                                 self.body[max(1, idx+1):])
                             for p in parts]
            return rewrites

        if strategy in ['normal', 'lo', 'leftmost-outermost']:
            head_attempt = rewrite_head()
            if head_attempt is not None:
                return head_attempt
            return rewrite_body()
        if strategy in ['eager', 'li', 'leftmost-innermost']:
            body_attempt = rewrite_body()
            if body_attempt is not None:
                return body_attempt
            return rewrite_head()
        if strategy in ['none', 'null']:
            head_attempt = rewrite_head()
            body_attempt = rewrite_all()
            if type == 'one':
                attempts = [a for a in body_attempt + [head_attempt]
                            if a is not None]
                return random.choice(attempts)
            ha = [] if head_attempt is None else head_attempt
            attempts = [a for a in ha + body_attempt if a is not None]
            return attempts


App = Application

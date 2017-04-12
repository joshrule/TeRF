"""
TRS.py - representations for Term Rewriting Systems

Written by: Joshua Rule <joshua.s.rule@gmail.com>
"""

counter = 0


def gensym():
    global counter
    counter += 1
    return '#g_' + str(counter)


class TRSError(Exception):
    pass


class Operator(object):
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
    def list_variables(self):
        raise NotImplementedError

    def list_operators(self):
        raise NotImplementedError


class Variable(Term):
    """an arbitrary term"""
    def __init__(self, name, identity=None):
        self.name = name
        self.identity = identity if identity else gensym()
        self.variables = self.list_variables()
        self.operators = self.list_operators()

    def list_variables(self):
        return {self}

    def list_operators(self):
        return set()

    def __str__(self):
        return self.name

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


class Application(Term):
    """a term applying an operator to arguments"""
    def __init__(self, head, body):
        try:
            if head.arity == len(body):
                self.head = head
                self.body = body
                self.variables = self.list_variables()
                self.operators = self.list_operators()
        except AttributeError:
            raise TRSError('head of term is a variable')

    def list_variables(self):
        return {variable for part in self.body for variable in part.variables}

    def list_operators(self):
        return {self.head} | \
               {operator for part in self.body for operator in part.operators}

    def __str__(self):
        if self.body:
            return '{}[{}]'.format(self.head,
                                   ', '.join([str(arg) for arg in self.body]))
        else:
            return str(self.head)

    def __repr__(self):
        return 'Application({},{})'.format(self.head, self.body)


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

    def __str__(self):
        return str(self.lhs) + ' -> ' + str(self.rhs)

    def __repr__(self):
        return 'RewriteRule({}, {})'.format(self.lhs, self.rhs)

    def list_variables(self):
        return self.lhs.list_variables() | self.rhs.list_variables()

    def list_operators(self):
        return self.lhs.list_operators() | self.rhs.list_operators()


class TRS(object):
    def __init__(self):
        self.signature = {}
        self.rules = []

    def add_operator(self, operator):
        try:
            name = '{}/{}'.format(operator.name, operator.arity)
        except AttributeError:
            raise TRSError('Tried to add a non-operator to a signature')
        else:
            self.signature[name] = operator

    def del_operator(self, name):
        del self.signature[name]

    def add_rule(self, rule):
        self.rules += [rule]

    def del_rule(self, idx):
        self.rules[idx] = None

    def __str__(self):
        return '[' + str(self.signature.keys()) + ',\n [' + \
            ',\n  '.join([str(rule) for rule in self.rules]) + ']]'

    # eval:
    # for n steps
    #  # perform a pre-order traversal of the term
    #  # at each node, attempt to evaluate
    #  # if successful, return to the top
    def eval(self, term, steps=1):
        count = 0
        while count < steps:
            term, changed = self.single_step(term)
            if changed:
                count += 1
            else:
                break
        return term

    def single_step(self, term, changed=False):
        if isinstance(term, Term):
            if not changed:
                for rule in [rule for rule in self.rules if rule is not None]:
                    sub = unify(rule.lhs, term, type='match')
                    if sub is not None:
                        return rewrite(rule.rhs, sub), True
                try:
                    for idx in range(len(term.body)):
                        term.body[idx], changed = \
                            self.single_step(term.body[idx], changed)
                        if changed:
                            break
                except AttributeError:
                    pass
            return term, changed
        else:
            raise TRSError('single_step: Can only evaluate terms')


def rewrite(term, sub):
    if isinstance(term, Variable):
        if term in sub:
            return sub[term]
        else:
            raise TRSError('rewrite: Variable has no definition!')
    elif isinstance(term, Application):
        return Application(term.head,
                           [rewrite(part, sub) for part in term.body])


def unify(t1, t2, env=-1, type='simple'):
    """unify two terms to produce a substitution

    t1, t2: Terms
    env: the substitution
    type: 'simple' is for unification, while 'match' is for rewriting
    """
    if env == -1:
        env = {}

    if isinstance(t1, Variable) and env is not None:
        return unify_var(t1, t2, env, type)

    elif isinstance(t2, Variable) and env is not None and type == 'simple':
        return unify_var(t2, t1, env, type)

    elif (isinstance(t1, Application) and
          isinstance(t2, Application) and
          t1.head == t2.head and
          env is not None):
        # unify each subterm
        for (st1, st2) in zip(t1.body, t2.body):
            env = unify(st1, st2, env, type)
        return env

    else:
        return None


def unify_var(t1, t2, env, type='simple'):
    if env is not None:
        if isinstance(t1, Variable):
            if t1 in env:
                unify(env[t1], t2, env, type)
            elif t2 in env:
                unify(t1, env[t2], env, type)
            else:
                if t1 == t2:
                    return env
                else:
                    env[t1] = t2
                    return env
        else:
            raise TRSError('unify-var: first arg must be a variable')
    else:
        return env

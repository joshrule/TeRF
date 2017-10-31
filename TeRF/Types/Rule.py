import collections
import itertools as I
import TeRF.Types.Term as T
import TeRF.Types.Application as A


class Rule(collections.MutableSet):
    def __init__(self, lhs, rhs, background=False):
        if isinstance(lhs, A.Application):
            self.lhs = lhs
            # ensure rhs is iterable of RHSs
            if isinstance(rhs, T.Term):
                rhs = [rhs]
            self.rhs = set()
            for case in rhs:
                if not isinstance(case, T.Term):
                    raise ValueError('Rule: rhs must be terms')
                try:
                    if self.lhs.variables >= case.variables:
                        self.rhs.add(case)
                    else:
                        raise ValueError('Rule: rhs invents variables')
                except AttributeError:
                    raise ValueError('Rule: rhs isn\'t a term')
        else:
            raise ValueError('Rule: lhs must be an application')

        self.background = background

    @property
    def variables(self):
        return self.lhs.variables

    @property
    def operators(self):
        return self.lhs.operators | {o for rhs in self.rhs
                                     for o in rhs.operators}

    @property
    def size(self):
        lhs_size = len(self.lhs)
        return sum(lhs_size + len(rhs) for rhs in self.rhs)

    def __contains__(self, item):
        # treat item as rule
        try:
            for item_rule in item:
                for self_rule in self:
                    if self_rule.unify(item_rule, type='alpha') is not None:
                        break
                else:
                    return False
            return True

        # treat item as term
        except (TypeError, AttributeError):
            for rhs in self.rhs:
                if rhs == item:
                    return True

        raise ValueError('Rule.__contains__: invalid query')

    def __len__(self):
        return len(self.rhs)

    def __iter__(self):
        for rhs in self.rhs:
            yield R(self.lhs, rhs)

    def __str__(self):
        lhs = self.lhs.to_string()
        rhs = ' | '.join(rhs.to_string() for rhs in self.rhs)
        return '{} = {}'.format(lhs, rhs)

    def __repr__(self):
        return 'Rule({}, {})'.format(self.lhs, self.rhs)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))

    def toggle(self):
        self.background = not self.background

    def add(self, item):
        # assume item is a rule
        try:
            env = item.lhs.unify(self.lhs, type='alpha')

        # assume item is a term
        except AttributeError:
            if self.lhs.variables >= item.variables:
                self.rhs.add(item)
        else:
            for rhs in item.rhs:
                self.rhs.add(rhs.substitute(env))

    def discard(self, item):
        # assume item is a rule
        try:
            env = item.lhs.unify(self.lhs, type='alpha')
            rhss = item.rhs.copy()
            for rhs in rhss:
                self.rhs.discard(rhs.substitute(env))
        except AttributeError:
            pass

        # assume item is a term
        self.rhs.discard(item)

    def unify(self, other, env=None, type='alpha'):
        env = self.lhs.unify(other.lhs, env=env, type=type)
        if len(self.rhs) == len(other.rhs):
            for srhs, orhs in I.izip(self.rhs, other.rhs):
                if env is not None:
                    env = srhs.unify(orhs, env=env, type=type)
            return env
        return None

    def parity(self, other, env=None):
        env = self.lhs.parity(other.lhs, env)
        if len(self.rhs) == len(other.rhs):
            for srhs, orhs in I.izip(self.rhs, other.rhs):
                if env is None:
                    break
                env = srhs.parity(orhs, env)
            return env
        return None

    def substitute(self, env):
        return Rule(self.lhs.substitute(env),
                    [rhs.substitute(env) for rhs in self.rhs])

    @property
    def rhs0(self):
        if len(self) == 1:
            return list(self.rhs)[0]
        raise ValueError('Rule.lone_rhs: multiple rhss')

    @property
    def complexity(self):
        return len(self.lhs) + sum(len(rhs) for rhs in self.rhs)

    def rename_variables(self):
        for i, v in enumerate(self.variables):
            v.name = 'v' + str(i)

    def log_p(self, grammar, start=None):
        return grammar.log_p_rule(self, start=start)


R = Rule

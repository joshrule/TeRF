import collections
import copy
import itertools as itertools
import TeRF.Types.Term as T
import TeRF.Types.Application as A


class Rule(collections.MutableSet):
    def __init__(self, lhs, rhs):
        if isinstance(lhs, A.Application):
            self.lhs = lhs
            # ensure rhs is iterable of RHSs
            if isinstance(rhs, T.Term):
                rhs = [rhs]
            self.rhs = []
            for case in rhs:
                if not isinstance(case, T.Term):
                    raise ValueError('Rule: rhs must be terms ' + str(case))
                try:
                    if self.lhs.variables() >= case.variables():
                        self.rhs.append(case)
                    else:
                        raise ValueError('Rule: rhs invents variables')
                except AttributeError:
                    raise ValueError('Rule: rhs isn\'t a term' + str(case))
        else:
            raise ValueError('Rule: lhs must be an application')

    def variables(self):
        return self.lhs.variables()

    def operators(self):
        try:
            return self._operators
        except AttributeError:
            self._operators = self.lhs.operators() | {o for rhs in self.rhs
                                                      for o in rhs.operators()}
            return self._operators

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
        if not hasattr(self, '_clauses'):
            self._clauses = [R(self.lhs, rhs) for rhs in self.rhs]
        for rule in self._clauses:
            yield rule

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

    def add(self, item):
        # assume item is a rule
        try:
            env = item.lhs.unify(self.lhs, type='alpha')

        # assume item is a term
        except AttributeError:
            if self.lhs.variables() >= item.variables():
                self.rhs.append(item)
        else:
            for rhs in item.rhs:
                self.rhs.append(rhs.substitute(env))

    def discard(self, item):
        # assume item is a rule
        try:
            env = item.lhs.unify(self.lhs, type='alpha')
            rhss = item.rhs[:]
            for rhs in rhss:
                srhs = rhs.substitute(env)
                if srhs in self.rhs:
                    self.rhs.remove(srhs)
        except AttributeError:
            pass

        # assume item is a term
        if item in self.rhs:
            self.rhs.remove(item)

    def unify(self, other, env=None, type='alpha'):
        env = self.lhs.unify(other.lhs, env=env, type=type)
        if len(self.rhs) == len(other.rhs):
            for srhs, orhs in itertools.izip(self.rhs, other.rhs):
                if env is not None:
                    env = srhs.unify(orhs, env=env, type=type)
            return env
        return None

    def substitute(self, env):
        return Rule(self.lhs.substitute(env),
                    [rhs.substitute(env) for rhs in self.rhs])

    @property
    def rhs0(self):
        if len(self) == 1:
            return self.rhs[0]
        raise ValueError('Rule.lone_rhs: multiple rhss')

    @property
    def complexity(self):
        return len(self.lhs) + sum(len(rhs) for rhs in self.rhs)

    def rename_variables(self):
        for i, v in enumerate(self.variables()):
            v.name = 'v' + str(i)

    def log_p(self, typesystem, target_type=None):
        if target_type is None:
            env = {v: typesystem.make_tv() for v in self.lhs.variables()}
            target_type = typesystem.type_rule(self,
                                               typesystem.make_env(env),
                                               {})
        lhs_log_p = len(self)*self.lhs.log_p(typesystem, target_type)
        rhs_log_p = sum(r.log_p(typesystem, target_type) for r in self.rhs)
        return lhs_log_p + rhs_log_p

    def places(self):
        return ([['lhs'] + p for p in self.lhs.places()] +
                [['rhs'] + [i] + p
                 for i, t in enumerate(self.rhs)
                 for p in t.places()])

    def place(self, place):
        if place[0] == 'lhs':
            return self.lhs.place(place[1:])
        return self.rhs[place[1]].place(place[2:])

    def replace(self, place, term):
        if place[0] == 'lhs':
            lhs = self.lhs.replace(place[1:], term)
            rhs = copy.deepcopy(self.rhs)
            return Rule(lhs, rhs)

        lhs = copy.deepcopy(self.lhs)
        rhs = self.rhs[place[1]].replace(place[2:], term)
        return Rule(lhs, rhs)


R = Rule

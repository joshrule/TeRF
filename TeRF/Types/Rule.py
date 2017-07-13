import collections as C
import itertools as I

import TeRF.Types.Term as T
import TeRF.Types.Application as A


class Rule(C.MutableSet):
    def __init__(self, lhs, rhs):
        if isinstance(lhs, A.Application):
            self.lhs = lhs
            self.signature = lhs.signature
            # ensure rhs is iterable of RHSs
            if isinstance(rhs, T.Term):
                rhs = [rhs]
            self.rhs = set()
            for case in rhs:
                try:
                    if self.signature.variables >= case.signature.variables:
                        self.rhs.add(case)
                        self.signature |= case.signature
                    else:
                        raise ValueError('Rule: rhs invents variables')
                except AttributeError:
                    raise ValueError('Rule: rhs isn\'t a term')
        else:
            raise ValueError('Rule: lhs must be an application')

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
        lhs = self.lhs.pretty_print()
        rhs = ' | '.join(rhs.pretty_print() for rhs in self.rhs)
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
            env = self.lhs.unify(item.lhs, type='alpha')
            self.rhs.add(item.rhs.substitute(env))

        # assume item is a term
        except (TypeError, AttributeError):
            if self.signature.variables >= item.signature.variables:
                self.rhs.add(item)
            else:
                raise ValueError('Rule.insert: rhs invents variables')

    def discard(self, item):
        # assume item is a rule
        try:
            env = self.lhs.unify(item.lhs, type='alpha')
            self.rhs.discard(item.rhs.substitute(env))
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


R = Rule

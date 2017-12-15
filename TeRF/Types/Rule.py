import collections
import TeRF.Algorithms.Substitute as s
import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.Unify as u
import TeRF.Types.Application as App
import TeRF.Types.Term as Term


class Rule(collections.MutableSet):
    def __init__(self, lhs, rhs):
        if isinstance(lhs, App.App):
            self.lhs = lhs
            if isinstance(rhs, Term.Term):
                rhs = [rhs]
            self.rhs = []
            for case in rhs:
                if not isinstance(case, Term.Term):
                    raise ValueError('Rule: non-term RHS: {!r}'.format(case))
                try:
                    if te.variables(self.lhs) >= te.variables(case):
                        self.rhs.append(case)
                    else:
                        raise ValueError('Rule: RHS invents variables: '
                                         '{!r}'.format(case))
                except AttributeError:
                    raise ValueError('Rule: non-term RHS: {!r}'.format(case))
        else:
            raise ValueError('Rule: non-application LHS: {!r}'.format(lhs))

    def __contains__(self, item):
        # treat item as rule
        try:
            for item_rule in item:
                for self_rule in self:
                    cs1 = ({(item_rule.lhs, self_rule.lhs)} |
                           {(rhs1, rhs2) for rhs1, rhs2 in zip(item_rule.rhs,
                                                               self_rule.rhs)})
                    cs2 = ({(self_rule.lhs, item_rule.lhs)} |
                           {(rhs1, rhs2) for rhs1, rhs2 in zip(self_rule.rhs,
                                                               item_rule.rhs)})
                    if u.unify(cs1, kind='match') is not None and \
                       u.unify(cs2, kind='match') is not None:
                        break
                else:
                    return False
            return True
        # treat item as term
        except (TypeError, AttributeError):
            for rhs in self.rhs:
                if rhs == item:
                    return True
        return False

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))

    def __iter__(self):
        for rhs in self.rhs:
            yield R(self.lhs, rhs)

    def __len__(self):
        return len(self.rhs)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'Rule(lhs={!r}, rhs={!r})'.format(self.lhs, self.rhs)

    def __str__(self):
        lhs = te.to_string(self.lhs)
        rhs = ' | '.join(te.to_string(rhs) for rhs in self.rhs)
        return '{} = {}'.format(lhs, rhs)

    @property
    def size(self):
        lhs_size = len(self.lhs)
        return sum(lhs_size + len(rhs) for rhs in self.rhs)

    @property
    def rhs0(self):
        if len(self) == 1:
            return self.rhs[0]
        raise ValueError('rhs0: too few/many RHSs: {!r}', len(self))

    def add(self, item):
        # assume item is a rule
        try:
            env = u.unify(item.lhs, self.lhs, kind='match')
            env2 = u.unify(self.lhs, item.lhs, kind='match')
        # assume item is a term
        except AttributeError:
            if te.variables(self.lhs) >= te.variables(item):
                self.rhs.append(item)
        else:
            if env is not None and env2 is not None:
                for rhs in item.rhs:
                    self.rhs.append(s.substitute(rhs, env))

    def discard(self, item):
        # assume item is a rule
        try:
            env = u.unify({(item.lhs, self.lhs)}, kind='match')
            env2 = u.unify({(self.lhs, item.lhs)}, kind='match')
            rhss = item.rhs[:]
            if env is not None and env2 is not None:
                for rhs in rhss:
                    srhs = s.substitute(rhs, env)
                    if srhs in self.rhs:
                        self.rhs.remove(srhs)
        # assume item is a term
        except AttributeError:
            if item in self.rhs:
                self.rhs.remove(item)


R = Rule

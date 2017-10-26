class Scope(object):
    def __init__(self, locked=True):
        self.locked = locked
        self._orig_locked = locked
        self.scope = {}

    def unlock(self):
        self.locked = False

    def lock(self):
        self.locked = True

    def reset(self):
        self.locked = self._orig_locked
        self.scope = {}

    def find(self, term):
        return [key
                for key in self.scope
                if self.scope[key] == term]

    def copy(self):
        s = Scope(locked=self.locked)
        s.scope = self.scope.copy()
        return s

    def __str__(self):
        scope_str = ', '.join(str(k) + ': ' + v.to_string()
                              for k, v in self.scope.items())
        return '({}, {{{}}})'.format(self.locked, scope_str)

    def __repr__(self):
        return str(self)

    def entails(self, other):
        """
        does self entail other?
        """
        return self.locked == other.locked and \
            all(other.scope[k] == v
                for k, v in self.scope.iteritems()
                if k in other.scope)

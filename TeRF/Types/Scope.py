import contextlib


@contextlib.contextmanager
def scope(grammar, scope=None, lock=None, reset=False, extend=None):
    stored_scope = grammar.scope.copy()
    if scope is not None:
        grammar.scope = scope.copy()
    if extend is not None:
        grammar.scope.scope.update(extend.scope)
    if reset:
        grammar.scope.reset()
    if lock is False:
        grammar.scope.unlock()
    elif lock is True:
        grammar.scope.lock()
    try:
        yield
    finally:
        grammar.scope = stored_scope


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

    def __eq__(self, other):
        return self.locked == other.locked and \
            self.scope == other.scope

    def __ne__(self, other):
        return not self == other

    def entails(self, other):
        """
        does self entail other?
        """
        return self.locked == other.locked and \
            all(other.scope[k] == v
                for k, v in self.scope.iteritems()
                if k in other.scope)


def merge_scopes(scopes):
    if scopes == []:
        return None
    scope = scopes[0].copy()
    for s in scopes:
        if s.locked == scope.locked:
            for k, v in s.scope.items():
                if k in scope.scope and scope.scope[k] != v:
                    return None
                elif k not in scope.scope:
                    scope.scope[k] = v
    return scope

from copy import copy
from itertools import izip
from numpy import argmin

from TeRF.TRS import App


class RewriteError(Exception):
    pass


def rewrite(trs, term, max_steps=1, trace=False):
    if trace:
        the_trace = [term]
    for _ in xrange(max_steps):
        term, changed, _ = single_rewrite(trs, term)
        if not changed:
            break
        if trace:
            the_trace.append(term)
    return the_trace if trace else term


def rewrites_to(trs, t1, t2, steps=100):
    nf_step = -1
    ts = [t1]
    for step in xrange(steps):
        t, changed, _ = single_rewrite(trs, ts[-1])
        if not changed:
            nf_step = step-1
            break
        ts.append(t)
    # distances = [edit_distance(t1, tree) for tree in ts]
    distances = [int(tree != t2) for tree in ts]
    min_step = argmin(distances)
    return min_step, distances[min_step], nf_step


def single_rewrite(trs, term):
    for rule in trs.rules:
        success, sub = unify(rule.lhs, term, type='match')
        if success and sub is not {}:
            new_term = substitute(copy(rule.rhs), sub)
            return new_term, (new_term != term), True

    try:
        for idx in xrange(len(term.body)):
            part, changed, stepped = single_rewrite(trs, term.body[idx])
            if stepped:
                new_term = App(term.head,
                               term.body[:max(0, idx)] +
                               [part] +
                               term.body[max(1, idx+1):])
                return new_term, changed, True
    except AttributeError:
        pass
    return term, False, False


def unify(t1, t2, env=None, type='simple'):
    """unify two terms to produce a substitution

    t1, t2: Terms
    env: the substitution
    type: 'simple' is for full unification
          'match' is for rewriting
          'alpha' is for alpha equivalence
    """
    try:  # treat t1 *and* t2 as applications
        if t1.head == t2.head:
            for (st1, st2) in izip(t1.body, t2.body):
                success, env = unify(st1, st2, env, type)
                if not success:
                    return False, None
            return True, env
        return False, None
    except AttributeError:
        pass

    try:  # treat t1 as variable
        return unify_var(t1, t2, env, type)
    except RewriteError:
        pass

    try:  # treat t2 as variable
        if type is 'simple':
            return unify_var(t2, t1, env, type)
    except RewriteError:
        pass
    return False, None


def unify_var(t1, t2, env, type='simple'):
    if hasattr(t1, 'identity'):
        if env is None:
            env = {}

        if t1 == t2:
            return True, env
        if t1 in env:
            return unify(env[t1], t2, env, type)
        if t2 in env:
            return unify(t1, env[t2], env, type)
        if type is not 'alpha' or hasattr(t2, 'identity'):
            env[t1] = t2
            return True, env
    else:
        raise RewriteError('unify_var: first arg must be a variable')


def substitute(term, sub):
    try:
        return App(term.head,
                   [substitute(part, sub) for part in term.body])
    except AttributeError:
        try:
            return sub[term]
        except KeyError:
            raise RewriteError('substitute: Variable has no definition!')

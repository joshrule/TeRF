from copy import copy
from itertools import repeat, izip
from numpy.random import choice

from TeRF.Terms import App


class RewriteError(Exception):
    pass


def rewrite(trs, term, max_steps=1, type='one'):
    if type == 'one':
        return rewrite_one(trs, term, max_steps)
    return rewrite_all(trs, term, max_steps)


def rewrite_all(trs, term, max_steps=1):
    terms = [term]
    for _ in repeat(None, max_steps):
        terms_out = []
        for t in terms:
            outcomes = single_rewrite(trs, t, type)
            terms_out += [t] if outcomes is None else outcomes
        terms = terms_out
        if terms_out == terms:
            break
    return terms


def rewrite_one(trs, term, max_steps=1):
    for _ in repeat(None, max_steps):
        term_out = single_rewrite(trs, term)
        if term_out is None or term == term_out:
            break
        term = term_out
    return term


def single_rewrite(trs, term, type='one'):
    """
    Perform a single rewrite of term using the TRS trs.

    Args:
      trs: a TRS a la TRS.py
      term: a Term a la TRS.py, the term to be rewritten
      type: how many possible rewrites to return either 'one' or 'all'
    Returns:
      None if no rewrite is possible, otherwise a single rewrite if type is
        'one' and all possible single rewrites if type is 'all'
    """
    for rule in trs.rules:
        sub = unify(rule.lhs, term, type='match')
        if sub is not None:
            return substitute(copy(rule.rhs), sub, type=type)

    try:
        for idx in xrange(len(term.body)):
            part = single_rewrite(trs, term.body[idx], type=type)
            if part is not None and type == 'one':
                return App(term.head,
                           term.body[:max(0, idx)] +
                           [part] +
                           term.body[max(1, idx+1):])
            if part is not None and type == 'all':
                return [App(term.head,
                            term.body[:max(0, idx)] +
                            [p] +
                            term.body[max(1, idx+1):])
                        for p in part]
    except AttributeError:
        pass
    return None


def unify(t1, t2, env=None, type='simple'):
    """
    unify two terms to produce a substitution

    Args:
      t1, t2: Terms
      env: the substitution
      type: 'simple' is for full unification
            'match' is for rewriting
            'alpha' is for alpha equivalence
    Returns:
      None if unification fails, else a dict representing the substitution
    """
    env = {} if env is None else env

    try:  # treat t1 *and* t2 as applications
        if t1.head == t2.head:
            for (st1, st2) in izip(t1.body, t2.body):
                env = unify(st1, st2, env, type)
                if env is None:
                    return env
            return env
        return None
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
        if t1 == t2:
            return env
        if t1 in env:
            return unify(env[t1], t2, env, type)
        if t2 in env:
            return unify(t1, env[t2], env, type)
        if type is not 'alpha' or hasattr(t2, 'identity'):
            env[t1] = t2
            return env
    raise RewriteError('unify_var: first arg must be a variable')


def substitute(terms, sub, type='one'):
    if type == 'one':
        terms = [choice(terms)]

    rets = []
    for term in terms:
        try:
            rets.append(App(term.head,
                            [substitute(part, sub) for part in term.body]))
        except AttributeError:
            try:
                rets.append(sub[term])
            except KeyError:
                raise RewriteError('substitute: Variable has no definition!')
    return rets[0] if type == 'one' else rets

import TeRF.Types.Application as A
import TeRF.Types.Variable as V
import TeRF.Algorithms.Substitute as S


def unify(cs, kind='unification'):
    """unify a set of constraints"""
    try:
        (s, t) = cs.pop()
    except KeyError:
        return {}

    if s == t:
        return unify(cs, kind=kind)
    elif isinstance(s, V.Variable) and s not in free_vars(t):
        return compose(unify(substitute(cs, {s: t}), kind=kind), {s: t})
    elif isinstance(t, V.Var) and t not in free_vars(s) and kind != 'match':
        return compose(unify(substitute(cs, {t: s}), kind=kind), {t: s})
    elif isinstance(s, A.App) and isinstance(t, A.App) and s.head == t.head:
        return unify(cs | set(zip(s.args, t.args)), kind=kind)
    return None


def free_vars(term):
    """compute the free variables in a term"""
    try:
        return {var for arg in term.args for var in free_vars(arg)}
    except AttributeError:
        return {term}


def compose(sub1, sub2):
    """compose two substitutions"""
    if sub1 is None or sub2 is None:
        return None
    sub = sub1.copy()
    sub.update({k: S.substitute(sub2[k], sub1) for k in sub2})
    return sub


def substitute(cs, sub):
    """substitution for a set of pairs"""
    return {(S.substitute(s, sub), S.substitute(t, sub)) for s, t in cs}


def alpha(t1, t2):
    result = unify({(t1, t2)}, kind='match')
    if result is not None and unify({(t2, t1)}, kind='match') is not None:
        return result
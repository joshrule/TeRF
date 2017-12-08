import TeRF.Types.Application as A
import TeRF.Types.Binding as B
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
        partial = unify(substitute(cs, {s: t}), kind=kind)
        return compose(partial, {s: t})
    elif isinstance(t, V.Var) and t not in free_vars(s) and kind != 'match':
        print 'what?'
        partial = unify(substitute(cs, {t: s}), kind=kind)
        return compose(partial, {t: s})
    elif isinstance(s, A.App) and isinstance(t, A.App) and s.head == t.head:
        arg_cs = {(st, tt) for st, tt in zip(s.args, t.args)}
        return unify(cs | arg_cs, kind=kind)
    return None


def free_vars(type, env=None):
    """compute the free variables in a term"""
    if isinstance(type, V.Variable):
        return {type} if env is None or type not in env.values() else set()
    elif isinstance(type, A.Application):
        return {var for arg in type.args for var in free_vars(arg, env=env)}
    elif isinstance(type, B.Binding):
        return free_vars(type, env=env).difference({type.bound})
    raise TypeError('not a term')


def compose(sub1, sub2):
    """compose two substitutions"""
    sub = sub1.copy()
    sub.update({k: S.substitute(sub2[k], sub1) for k in sub2})
    return sub


def substitute(cs, sub):
    """substitution for a set of pairs"""
    return {(S.substitute(s, sub), S.substitute(t, sub)) for s, t in cs}

import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.TypeUtils as ty


def unify(cs, kind='unification'):
    """unify a set of constraints"""
    try:
        (s, t) = cs.pop()
    except KeyError:
        return {}

    if s == t:
        return unify(cs, kind=kind)
    elif isinstance(s, TVar.TVar) and s not in free_vars(t):
        partial = unify(substitute(cs, {s: t}), kind=kind)
        return compose(partial, {s: t})
    elif (isinstance(t, TVar.TVar) and
          t not in free_vars(s) and
          kind != 'match'):
        partial = unify(substitute(cs, {t: s}), kind=kind)
        return compose(partial, {t: s})
    elif (isinstance(s, TOp.TOp) and
          isinstance(t, TOp.TOp) and
          s.head == t.head):
        arg_cs = {(st, tt) for st, tt in zip(s.args, t.args)}
        return unify(cs | arg_cs, kind=kind)
    return None


def free_vars(type, env=None):
    """compute the free variables in a term"""
    if isinstance(type, TVar.TVar):
        return {type} if env is None or type not in env.values() else set()
    elif isinstance(type, TOp.TOp):
        return {var for arg in type.args for var in free_vars(arg, env=env)}
    elif isinstance(type, TBind.TBind):
        return free_vars(type, env=env).difference({type.bound})
    raise TypeError('not a term')


def compose(sub1, sub2):
    """compose two substitutions"""
    if sub1 is None or sub2 is None:
        raise TypeError('invalid substitution')
    sub1.update({k: ty.substitute(sub2[k], sub1) for k in sub2})
    return sub1


def substitute(cs, sub):
    """substitution for a set of pairs"""
    return {(ty.substitute(s, sub), ty.substitute(t, sub)) for s, t in cs}

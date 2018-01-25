import itertools
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Types.TypeVariable as TVar


def size(trs):
    return sum(r.size for r in trs)


def unifies(trs1, trs2, kind='unification'):
    if len(trs1) == len(trs2):
        for r1, r2 in itertools.zip_longest(trs1, trs2):
            if ru.unify(r1, r2, kind=kind) is None:
                return False
        return True
    return False


def alphas(trs1, trs2):
    result = unifies(trs1, trs2, kind='match')
    if result is not None and unifies(trs2, trs1, kind='match') is not None:
        return result


def typecheck(trs, env, sub):
    return typecheck_full(trs, env, sub)[0]


def typecheck_full(trs, env, sub):
    for rule in trs:
        env2 = env.copy()
        env2.update({v: TVar.TVar() for v in ru.variables(rule)})
        try:
            _, sub = ru.typecheck_full(rule, env2, sub)
        except ValueError:
            raise ValueError('untypable: {!r}'.format(trs))
        if sub is None:
            raise ValueError('untypable: {!r}'.format(trs))
    return sub

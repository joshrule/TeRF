import itertools
import TeRF.Algorithms.RuleUtils as ru


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

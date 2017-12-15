import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.Substitute as s
import TeRF.Algorithms.TypeUnify as u
import TeRF.Types.Rule as Rule


def variables(rule):
    return te.variables(rule.lhs)


def operators(rule):
    return te.operators(rule.lhs) | {o for rhs in rule.rhs
                                     for o in te.operators(rhs)}


def places(rule):
    return ([['lhs'] + p for p in te.places(rule.lhs)] +
            [['rhs', i] + p
             for i, rhs in enumerate(rule.rhs)
             for p in te.places(rhs)])


def place(rule, place):
    if place[0] == 'lhs':
        return te.subterm(rule.lhs, place[1:])
    return te.subterm(rule.rhs[place[1]], place[2:])


def replace(rule, place, term):
    if place[0] == 'lhs':
        return Rule.Rule(te.replace(rule.lhs, place[1:], term), rule.rhs[:])
    return Rule.Rule(rule.lhs, te.replace(rule.rhs[place[1]], place[2:], term))


def unify(r1, r2, kind='unification'):
    return u.unify({(r1.lhs, r2.lhs)} |
                   {(rhs1, rhs2) for rhs1, rhs2 in zip(r1.rhs, r2.rhs)})


def alpha(r1, r2):
    result = unify(r1, r2, kind='match')
    if result is not None and unify(r2, r1, kind='match') is not None:
        return result


def substitute(rule, env):
    return Rule.Rule(s.substitute(rule.lhs, env),
                     [s.substitute(rhs, env) for rhs in rule.rhs])


def rename_variables(rule):
    for i, v in enumerate(variables(rule)):
        v.name = 'v' + str(i)


def typecheck(self, env, sub):
    lhs_type = ty.specialize(tc.typecheck(self.lhs, env, sub))
    rhs_types = [ty.specialize(tc.typecheck(rhs, env.copy(), sub))
                 for rhs in self.rhs]
    new_sub = u.unify({(lhs_type, rhs_type) for rhs_type in rhs_types})
    if new_sub is not None:
        return ty.update(lhs_type, env, u.compose(new_sub, sub))
    raise ValueError('untypable: ' + str(self))

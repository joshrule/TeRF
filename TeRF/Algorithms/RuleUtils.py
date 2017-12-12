import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.Substitute as s
import TeRF.Algorithms.Unify as u
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
        return te.place(rule.lhs, place[1:])
    return te.place(rule.rhs[place[1]], place[2:])


def replace(rule, place, term):
    if place[0] == 'lhs':
        return Rule(te.replace(rule.lhs, place[1:], term), rule.rhs[:])
    return Rule(rule.lhs, te.replace(rule.rhs[place[1]], place[2:], term))


def unify(r1, r2, env=None, kind='unification'):
    return u.unify({(r1.lhs, r2.lhs)} |
                   {(rhs1, rhs2) for rhs1, rhs2 in zip(r1.rhs, r2.rhs)})


def substitute(rule, env):
    return Rule.Rule(s.substitute(rule.lhs, env),
                     [s.substitute(rhs, env) for rhs in rule.rhs])


def rename_variables(rule):
    for i, v in enumerate(variables(rule)):
        v.name = 'v' + str(i)


# def sample_rule():
#     pass
#
# def log_p(self, typesystem, target_type=None):
#     if target_type is None:
#         env = {v: typesystem.make_tv() for v in self.lhs.variables()}
#         target_type = typesystem.type_rule(self,
#                                            typesystem.make_env(env),
#                                            {})
#     lhs_log_p = len(self)*self.lhs.log_p(typesystem, target_type)
#     rhs_log_p = sum(r.log_p(typesystem, target_type) for r in self.rhs)
#     return lhs_log_p + rhs_log_p
#
#
# def typecheck(self, env, sub):
#     lhs_type = self.lhs.typecheck(env, sub).specialize()
#     rhs_types = [rhs.typecheck(env.copy(), sub).specialize()
#                  for rhs in self.rhs]
#     new_sub = unify({(lhs_type, rhs_type) for rhs_type in rhs_types})
#     if new_sub is not None:
#         return lhs_type.substitute(new_sub).generalize(
#             env.substitute(new_sub.compose(sub)))
#     raise ValueError('untypable: ' + str(self))

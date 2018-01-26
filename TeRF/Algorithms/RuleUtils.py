import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.Substitute as s
import TeRF.Algorithms.TypeUnify as u
import TeRF.Algorithms.Unify as uni
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


def subterms(rule):
    for subterm in te.subterms(rule.lhs):
        yield subterm
    for rhs in rule.rhs:
        for subterm in te.subterms(rhs):
            yield subterm


def replace(rule, place, term, template=False):
    if place[0] == 'lhs':
        return Rule.Rule(te.replace(rule.lhs, place[1:], term), rule.rhs[:],
                         template)
    return Rule.Rule(rule.lhs, te.replace(rule.rhs[place[1]], place[2:], term),
                     template)


def unify(r1, r2, kind='unification'):
    return uni.unify({(r1.lhs, r2.lhs)} |
                     {(rhs1, rhs2) for rhs1, rhs2 in zip(r1.rhs, r2.rhs)},
                     kind=kind)


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
    return typecheck_full(self, env, sub)[0]


def typecheck_full(self, env, sub):
    lhs_type_scheme, sub = tc.typecheck_full(self.lhs, env, sub)
    lhs_type = ty.specialize_top(lhs_type_scheme)
    rhs_types = []
    for rhs in self.rhs:
        rhs_type, sub = tc.typecheck_full(rhs, env, sub)
        rhs_types.append(ty.specialize_top(rhs_type))
    new_sub = u.unify({(lhs_type, rhs_type) for rhs_type in rhs_types})
    # print 'lhs_type', lhs_type
    # print 'rhs_types', rhs_types
    # print 'old_sub'
    # for k, v in sub.items():
    #     print '   ', k, ':', v
    # print 'new_sub'
    # if new_sub is not None:
    #     for k, v in new_sub.items():
    #         print '   ', k, ':', v
    # else:
    #     print '   None'
    try:
        final_sub = u.compose(new_sub, sub)
        # print 'ru.final_sub'
        # for k, v in final_sub.items():
        #     print '   ', k, ':', v
    except TypeError:
        raise ValueError('untypable: ' + str(self))
    return ty.update(lhs_type, env, final_sub), final_sub


def typecheck_subterm(self, env, sub, place):
    if place[0] == 'lhs':
        lhs_type_scheme, sub, subtype = tc.typecheck_subterm(
            self.lhs, env, sub, place[1:])
    else:
        lhs_type_scheme, sub = tc.typecheck_full(self.lhs, env, sub)
    lhs_type = ty.specialize_top(lhs_type_scheme)

    rhs_types = []
    for i, rhs in enumerate(self.rhs):
        if place[0] == 'rhs' and place[1] == i:
            rhs_type_scheme, _, subtype = tc.typecheck_subterm(
                rhs, env, sub.copy(), place[2:])
            rhs_types.append(ty.specialize_top(rhs_type_scheme))
        else:
            rhs_types.append(ty.specialize_top(tc.typecheck(rhs, env,
                                                            sub.copy())))

    new_sub = u.unify({(lhs_type, rhs_type) for rhs_type in rhs_types})
    final_sub = u.compose(new_sub, sub)
    if final_sub is not None:
        return ty.update(lhs_type, env, final_sub), final_sub, subtype
    raise ValueError('untypable: ' + str(self))

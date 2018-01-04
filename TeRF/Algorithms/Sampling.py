import copy
import numpy as np
import scipy.stats as stats
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as App
import TeRF.Types.Hole as Hole
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as Rule
import TeRF.Types.Variable as Var
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.TypeUnify as tu


class SampleError(Exception):
    pass


def sample_term(target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    if d > max_d:
        raise SampleError('depth bound {} < {}'.format(max_d, d))
    options = np.random.permutation(list(gen_options(target_type, env, sub,
                                                     invent)))
    for o in options:
        try:
            return try_option(*o, invent=invent, max_d=max_d, d=d)
        except SampleError:
            pass
    raise SampleError('failed to sample term')


def try_option(atom, body_types, env, sub, invent, max_d, d):
    if isinstance(atom, Var.Var):
        return atom, env, sub
    subterms = []
    constraints = set()
    for i, bt in enumerate(body_types):
        sub = tu.compose(tu.unify(constraints.copy()), sub)
        subtype = ty.substitute([bt], sub)[0]
        d_i = (d+1)*(i == 0)
        subterm, env, sub = sample_term(subtype, env, sub, invent, max_d, d_i)
        subterms.append(subterm)
        final_type = ty.specialize(tc.typecheck(subterm, env, sub))
        constraints.add((subtype, final_type))
    sub = tu.compose(tu.unify(constraints.copy()), sub)
    return App.App(atom, subterms), env, sub


def gen_options(target_type, env, sub, invent):
    for atom in env:
        option = check_option(atom, target_type, env, sub)
        if option is not None:
            yield option
    if invent:
        yield invent_variable(target_type, env, sub)


def invent_variable(target_type, env, sub):
    var = Var.Var()
    env2 = copy.copy(env)
    env2[var] = target_type
    return var, [], env2, sub


def check_option(atom, target_type, env, sub):
    if isinstance(atom, Var.Var):
        result_type = ty.update(env[atom], env, sub)
        body_types = []
        constraints = set()

    elif isinstance(atom, Op.Op):
        head_type = ty.specialize(ty.update(env[atom], env, sub))
        body_types = [TVar.TVar() for _ in xrange(atom.arity)]
        result_type = TVar.TVar()
        constraints = {(head_type,
                        ty.multi_argument_function(body_types,
                                                   result=result_type))}

    spec_type = ty.specialize(target_type)
    try:
        unification = tu.unify(constraints | {(result_type, spec_type)})
        sub2 = tu.compose(unification, sub)
    except TypeError:
        return None
    return atom, body_types, env, sub2


def lp_term(term, target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    if d > max_d:
        return -np.inf, env, sub

    options = list(gen_options(target_type, env, sub, False))
    if invent:
        if isinstance(term, Var.Var) and term not in env:
            env2 = copy.copy(env)
            env2[term] = target_type
            options.append([term, [], env2, sub])
        else:
            options.append([Var.Var('BOGUS'), [], env, sub])
    matches = [o for o in options if o[0] == term.head]
    if len(matches) > 1:
        raise ValueError('bad environment: {!r}'.format(env))

    lp = misc.logNof(options, n=len(matches))

    if lp == -np.inf:
        return lp, env, sub

    atom, body_types, env, sub = matches[0]

    if isinstance(atom, Var.Var):
        return lp, env, sub

    lps = [lp]
    constraints = set()
    for i, (subterm, body_type) in enumerate(zip(term.args, body_types)):
        try:
            sub = tu.compose(tu.unify(constraints.copy()), sub)
        except TypeError:
            return -np.inf, env, sub
        subtype = ty.substitute([body_type], sub)[0]
        d_i = (d+1)*(i == 0)
        lp, env, sub = lp_term(subterm, subtype, env, sub, invent, max_d, d_i)
        lps.append(lp)
        final_type = ty.specialize(tc.typecheck(subterm, env, sub))
        constraints.add((subtype, final_type))
    try:
        sub = tu.compose(tu.unify(constraints.copy()), sub)
    except TypeError:
        return -np.inf, env, sub
    return sum(lps), env, sub


def sample_rule(target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    lhs = None
    while not isinstance(lhs, App.App):
        lhs, env2, sub2 = sample_term(target_type, env, sub.copy(),
                                      invent, max_d, d)
    rhs, _, _ = sample_term(target_type, env2, sub2, invent=False,
                            max_d=max_d, d=d)
    return Rule.Rule(lhs, rhs)


def lp_rule(rule, target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    lp_lhs, env, sub = lp_term(rule.lhs, target_type, env, sub, invent,
                               max_d, d)
    lp_rhs, _, _ = lp_term(rule.rhs0, target_type, env, sub, False, max_d, d)
    return lp_lhs + lp_rhs


def lp_trs(trs, env, p_rule, types, invent=False):
    p_n_rules = stats.geom.logpmf(len(trs.clauses)+1, p=p_rule)
    p_rules = 0
    p_rules = sum(misc.logsumexp([lp_rule(rule, t, env, invent=invent)
                                  for t in types])
                  for rule in trs.clauses)
    return p_n_rules + p_rules


def fill_template(template, env, sub):
    rule = copy.deepcopy(template)
    t_type, sub = ru.typecheck_full(rule, env, sub)
    replacements = []
    for place in ru.places(rule):
        subterm = ru.place(rule, place)
        if isinstance(subterm, Hole.Hole):
            invent = place[0] == 'lhs'
            target_type, sub = tc.typecheck_full(subterm, env, sub)
            term, env, sub = sample_term(target_type, env, sub, invent=invent)
            replacements.append((place, term))
    for place, term in replacements:
        rule = ru.replace(rule, place, term)
    return rule


def lp_template(rule, template, env, sub, invent=False):
    t_type, sub = ru.typecheck_full(template, env, sub)
    for place in ru.places(template):
        subtemplate = ru.place(template, place)
        try:
            subrule = ru.place(rule, place)
        except ValueError:
            return -np.inf
        lp = 0
        if isinstance(subtemplate, Hole.Hole):
            invent = place[0] == 'lhs'
            target_type, sub = tc.typecheck_full(subtemplate, env, sub)
            lt, env, sub = lp_term(subrule, target_type, env, sub,
                                   invent=invent)
            lp += lt
    return lp

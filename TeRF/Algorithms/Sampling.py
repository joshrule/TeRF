import copy
import numpy as np
import scipy.stats as stats
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as App
import TeRF.Types.Hole as Hole
import TeRF.Types.Rule as Rule
import TeRF.Types.Variable as Var
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.TypeUnify as tu


class SampleError(Exception):
    pass


def sample_term(target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    if d > max_d:
        raise SampleError('depth bound {} < {}'.format(max_d, d))
    apps, vs = gen_options(target_type, env, sub, invent)
    # TODO: Total HACK!
    app_ps = [.5/len(apps)]*len(apps) if len(apps) else []
    v_ps = [.5/len(vs)]*len(vs) if len(vs) else []
    ps = misc.normalize(app_ps + v_ps)
    order = np.random.choice(len(ps), p=ps, replace=False, size=len(ps))
    options = apps + vs
    for idx in order:
        o = options[idx]
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
        subtype = ty.substitute(bt, sub)
        d_i = (d+1)*(i == 0)
        subterm, env, sub = sample_term(subtype, env, sub, invent, max_d, d_i)
        subterms.append(subterm)
        final_type = ty.specialize_top(tc.typecheck(subterm, env, sub))
        constraints.add((subtype, final_type))
    sub = tu.compose(tu.unify(constraints.copy()), sub)
    return App.App(atom, subterms), env, sub


def gen_options(target_type, env, sub, invent):
    options = []
    tt = ty.specialize_top(target_type)
    for atom in env:
        option = check_option(atom, tt, env, sub)
        if option is not None:
            options.append(option)
    if invent:
        options.append(invent_variable(tt, env, sub))
    apps, vs = [], []
    for option in options:
        apps.append(option) if hasattr(option[0], 'arity') else vs.append(option)
    return apps, vs


def invent_variable(target_type, env, sub):
    var = Var.Var()
    env2 = copy.copy(env)
    env2[var] = target_type
    return var, [], env2, sub


def check_option(atom, target_type, env, sub):
    try:
        body_types = [TVar.TVar() for _ in xrange(atom.arity)]
    except AttributeError:
        body_types = []
        result_type = ty.update2(env[atom], sub)
        constraints = set()
    else:
        result_type = TVar.TVar()
        head_type = ty.update2(env[atom], sub)
        constraints = {(head_type,
                        ty.multi_argument_function(body_types, result_type))}

    try:
        new_sub = tu.unify(constraints | {(result_type, target_type)})
        return atom, body_types, env, tu.compose(new_sub, sub)
    except TypeError:
        return None


def lp_term(term, target_type, env, sub=None, invent=False, max_d=5, d=0):
    # print 'lp_term'
    # print '  term', term
    # print '  target_type', target_type
    sub = {} if sub is None else sub
    if d > max_d or any(a not in env and not invent for a in te.atoms(term)):
        return -np.inf, env, sub

    apps, vs = gen_options(target_type, env, sub, False)
    if invent:
        if isinstance(term, Var.Var) and term not in env:
            env2 = copy.copy(env)
            env2[term] = target_type
            # print 'adding', term, 'as', target_type
            vs.append([term, [], env2, sub])
        else:
            vs.append([Var.Var('BOGUS'), [], env, sub])
    options = apps + vs
    matches = [o for o in options if o[0] == term.head]
    if len(matches) > 1:
        raise ValueError('bad environment: {!r}'.format(env))

    # TODO: Total HACK!
    if len(matches) == 0:
        return -np.inf, env, sub
    elif hasattr(matches[0][0], 'arity'):
        lp = np.log(0.5)-np.log(len(apps))
    else:
        lp = np.log(0.5)-np.log(len(vs))

    # print 'match', matches[0]
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
        subtype = ty.substitute(body_type, sub)
        d_i = (d+1)*(i == 0)
        lp, env, sub = lp_term(subterm, subtype, env, sub, invent, max_d, d_i)
        lps.append(lp)
        final_type = ty.specialize_top(tc.typecheck(subterm, env, sub))
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


def fill_template(template, env, sub, invent=False):
    rule = copy.deepcopy(template)
    temp_env = copy.deepcopy(env)
    for place in ru.places(rule):
        subterm = ru.place(rule, place)
        if isinstance(subterm, Hole.Hole) and subterm not in temp_env:
            temp_env[subterm] = TVar.TVar()
    # flip a biased coin and just use the type if the flip fails
    if np.random.random() > 0.99:
        t_type, sub = ru.typecheck_full(template, temp_env, sub)
        return sample_rule(t_type, env, sub, invent=invent)
    t_type, sub = ru.typecheck_full(rule, temp_env, sub)
    replacements = []
    for place in ru.places(rule):
        subterm = ru.place(rule, place)
        if isinstance(subterm, Hole.Hole):
            i_here = place[0] == 'lhs' and invent
            target_type, sub = tc.typecheck_full(subterm, temp_env, sub)
            term, env, sub = sample_term(target_type, env, sub, invent=i_here)
            replacements.append((place, term))
    for place, term in replacements:
        rule = ru.replace(rule, place, term, True)
    return rule


def lp_template(rule, template, env, sub, invent=False):
    # make sure the rule is compatible with the template
    if ru.unify(template, rule, kind='match') is None:
        return -np.inf
    temp_env = env.copy()
    for subterm in ru.subterms(template):
        if isinstance(subterm, Hole.Hole) and subterm not in temp_env:
            temp_env[subterm] = TVar.TVar()
    t_type, sub2 = ru.typecheck_full(template, temp_env, sub)
    p_rule = lp_rule(rule, t_type, env, sub)
    sub = sub2
    for place in ru.places(template):
        subtemplate = ru.place(template, place)
        try:
            subrule = ru.place(rule, place)
        except ValueError:
            return misc.logsumexp([-np.inf, misc.log(0.01)+p_rule])
        lp = 0
        if isinstance(subtemplate, Hole.Hole):
            invent = place[0] == 'lhs'
            target_type, sub = tc.typecheck_full(subtemplate, temp_env, sub)
            lt, env, sub = lp_term(subrule, target_type, env, sub,
                                   invent=invent)
            lp += lt
    return misc.logsumexp([misc.log(0.99)+lp, misc.log(0.01)+p_rule])

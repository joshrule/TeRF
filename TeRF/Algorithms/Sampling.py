import numpy as np
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as App
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as Rule
import TeRF.Types.Variable as Var
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.Typecheck as tc
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
        subtype = ty.substitute(bt, sub)
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
    env2 = env.copy()
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


def log_p_term(term, target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    if d > max_d:
        return -np.inf, env, sub

    options = list(gen_options(target_type, env, sub, invent))
    matches = [o for o in options if o[0] == term.head]
    if len(matches) > 1:
        raise ValueError('bad environment: {!r}'.format(env))

    log_p = misc.logNof(options, n=len(matches))

    if log_p == -np.inf:
        return log_p, env, sub

    atom, body_types, env, sub = matches[0]

    if isinstance(atom, Var.Var):
        return log_p, env, sub

    log_ps = [log_p]
    constraints = set()
    for i, (subterm, body_type) in enumerate(zip(term.args, body_types)):
        sub = tu.compose(tu.unify(constraints.copy()), sub)
        subtype = ty.substitute(body_type, sub)
        d_i = (d+1)*(i == 0)
        log_p, env, sub = log_p_term(subterm, subtype, env, sub,
                                     invent, max_d, d_i)
        log_ps.append(log_p)
        final_type = ty.specialize(tc.typecheck(subterm, env, sub))
        constraints.add((subtype, final_type))
    sub = tu.compose(tu.unify(constraints.copy()), sub)
    return sum(log_ps), env, sub


def sample_rule(target_type, env, sub=None, invent=False, max_d=5, d=0):
    sub = {} if sub is None else sub
    lhs = None
    while not isinstance(lhs, App.App):
        lhs, env2, sub2 = sample_term(target_type, env.copy(), sub.copy(),
                                      invent, max_d, d)
    rhs, _, _ = sample_term(target_type, env2, sub2, invent=False,
                            max_d=max_d, d=d)
    return Rule.Rule(lhs, rhs)

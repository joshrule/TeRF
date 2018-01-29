"""
Hindley-Milner Typing for First-Order Term Rewriting Systems (no abstraction)

Much thanks to:
- https://github.com/rob-smallshire/hindley-milner-python
- https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system
- (TAPL; Pierce, 2002, ch. 22)
"""

import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.TypeUnify as tu


def typecheck(term, typesystem, sub):
    the_type, the_sub = typecheck_full(term, typesystem, sub)
    return the_type


def typecheck_full(term, env, sub):
    the_type, the_sub = typecheck_full_helper(term, env, sub)
    # hard-coded variable substitution here saves time
    fvs = {v
           for x in ty.free_vars_in_env(env)
           for v in ty.free_vars(the_sub.get(x, x))}
    return ty.generalize(the_type, fvs), the_sub


def typecheck_full_helper(term, env, sub):
    try:
        if term.head.arity == 0:
            return ty.update2(env[term.head], sub), sub
    except AttributeError:
        return ty.update2(env[term.head], sub), sub

    body_type, sub = typecheck_args(term.args, env, sub)
    head_type = ty.update2(env[term.head], sub)
    try:
        blah_sub = tu.unify({(head_type, body_type)})
        sub = tu.compose(blah_sub, sub)
    except TypeError as err:
        print 'caught TypeError:', err
        raise ValueError('untypable: ' + str(term))
    return ty.update2(ty.result_type(body_type), sub), sub


def typecheck_args(args, env, sub):
    pre_types = []
    for a in args:
        pre_type, sub = typecheck_full_helper(a, env, sub)
        pre_types.append(pre_type)
    body_type = ty.multi_argument_function(pre_types)
    return body_type, sub


def typecheck_subterm(term, env, sub, place):
    fulltype, sub, subtype = typecheck_subterm_helper(term, env, sub, place)
    fvs = {v
           for x in ty.free_vars_in_env(env)
           for v in ty.free_vars(sub.get(x, x))}
    return ty.generalize(fulltype, fvs), sub, ty.generalize(subtype, fvs)


def typecheck_subterm_helper(term, env, sub, target_place):
    try:
        if term.head.arity == 0:
            the_type = ty.update2(env[term.head], sub)
            if target_place == []:
                return the_type, sub, the_type
            raise ValueError('bad subterm')
    except AttributeError:
        the_type = ty.update2(env[term.head], sub)
        if target_place == []:
            return the_type, sub, the_type
        raise ValueError('bad subterm')

    head_type = ty.update2(env[term.head], sub)
    body_type, sub, subtype = typecheck_subterm_args(
        term.args, env, sub, target_place)
    try:
        sub = tu.compose(tu.unify({(head_type, body_type)}), sub)
    except TypeError:
        raise ValueError('untypable: ' + repr(term))
    the_type = ty.update2(ty.result_type(body_type), sub)
    if target_place == []:
        return the_type, sub, the_type
    subtype = ty.update2(subtype, sub)
    return the_type, sub, subtype


def typecheck_subterm_args(args, env, sub, target_place):
    pre_types = []
    subtype = None
    for i, a in enumerate(args):
        if target_place == [] or i != target_place[0]:
            pre_type, sub = typecheck_full_helper(a, env, sub)
        else:
            pre_type, sub, subtype = typecheck_subterm_helper(
                a, env, sub, target_place[1:])
        pre_types.append(pre_type)
    body_type = ty.multi_argument_function(pre_types)
    return body_type, sub, subtype

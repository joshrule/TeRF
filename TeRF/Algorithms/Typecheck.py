"""
Hindley-Milner Typing for First-Order Term Rewriting Systems (no abstraction)

Much thanks to:
- https://github.com/rob-smallshire/hindley-milner-python
- https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system
- (TAPL; Pierce, 2002, ch. 22)
"""

import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUnify as tu


@te.term_decorator
def typecheck(term, typesystem, sub):
    the_type, the_sub = typecheck_full(term, typesystem, sub)
    return the_type


def typecheck_full(term, env, sub):
    try:
        if term.head.arity == 0:
            return ty.update(env[term.head], env, sub), sub
    except AttributeError:
        return ty.update(env[term.head], env, sub), sub

    head_type = ty.substitute([ty.specialize(env[term.head])], sub)[0]
    body_type, sub = typecheck_args(term.args, env, sub)

    try:
        sub = tu.compose(tu.unify({(head_type, body_type)}), sub)
    except TypeError:
        raise ValueError('untypable: ' + te.to_string(term))
    return ty.update(ty.result_type(body_type), env, sub), sub


def typecheck_args(args, env, sub):
    pre_types = []
    for a in args:
        gen_type, sub = typecheck_full(a, env, sub)
        pre_type = ty.substitute([ty.specialize(gen_type)], sub)[0]
        pre_types.append(pre_type)
    body_type = ty.multi_argument_function(pre_types, result='var')
    return body_type, sub

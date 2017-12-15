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
def typecheck(term, env, sub):
    try:
        if term.head.arity == 0:
            return ty.update(env[term.head], env, sub)
    except AttributeError:
        return ty.update(env[term], env, sub)
    else:
        head_type = ty.substitute(ty.specialize(env[term.head]), sub)
        pre_types = [ty.specialize(typecheck(a, env, sub)) for a in term.args]
        body_type = ty.multi_argument_function(pre_types)
        try:
            tu.compose(sub, tu.unify({(head_type, body_type)}))
        except TypeError:
            raise ValueError('untypable: ' + te.to_string(term))
        return ty.update(ty.result_type(body_type), env, sub)

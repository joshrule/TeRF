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


# Type checking doesn't work right now because the unify algorithm is written
# for TRS terms, rather than for more type terms. I can duplicate all the code,
# or I can reorganize again. I'll duplicate the code for now.


@te.term_decorator
def typecheck(term, env, sub):
    print 'term', te.to_string(term)
    try:
        if term.head.arity == 0:
            type = ty.update(env[term.head], env, sub)
            print 'type (constant)', type
            return type
    except AttributeError:
        type = ty.update(env[term], env, sub)
        print 'type (variable)', type
        return type
    else:
        head_type = ty.substitute(ty.specialize(env[term.head]), sub)
        print 'head_type', head_type
        pre_types = [ty.specialize(typecheck(a, env, sub)) for a in term.args]
        body_type = ty.multi_argument_function(pre_types)
        print 'body_type', body_type
        try:
            tu.compose(sub, tu.unify({(head_type, body_type)}))
        except TypeError:
            raise ValueError('untypable: ' + te.to_string(term))
        type = ty.update(ty.result_type(body_type), env, sub)
        print 'type (application)', type
        return type

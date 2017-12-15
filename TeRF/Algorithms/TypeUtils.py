import TeRF.Types.TypeVariable as TVar
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind


def multi_argument_function(arg_types, result='var'):
    arg_types = arg_types[:]
    if result == 'last':
        f_type = arg_types.pop()
    elif result == 'var':
        f_type = TVar.TVar()
    else:
        f_type = result
    while len(arg_types) > 0:
        f_type = function(arg_types.pop(), f_type)
    return f_type


def function(arg1, arg2):
    return TOp.TOp('->', [arg1, arg2])


def is_function(type):
    try:
        return type.head == '->' and len(type.args) == 2
    except AttributeError:
        return False


def result_type(type, final=True):
    if is_function(type):
        f_type = type
        while is_function(f_type):
            f_type = f_type.args[1]
        return f_type
    raise ValueError('not a function {!r}'.format(type))


def generalize(type, bound=None):
    the_type = type
    for v in free_vars(type, bound):
        the_type = TBind.TBind(v, the_type)
    return the_type


def specialize(type, env=None):
    env = {} if env is None else env
    if isinstance(type, TVar.TVar):
        try:
            return env[type]
        except KeyError:
            return type
    if isinstance(type, TOp.TOp):
        return TOp.TOp(type.head, [specialize(arg, env) for arg in type.args])
    if isinstance(type, TBind.TBind):
        if type.variable not in env:
            env[type.variable] = TVar.TVar()
        return specialize(type.body, env)
    return TypeError('not a type')


def substitute(type, sub):
    if isinstance(type, TVar.TVar):
        return sub[type] if type in sub else type
    if isinstance(type, TOp.TOp):
        return TOp.TOp(type.head, [substitute(arg, sub) for arg in type.args])
    if isinstance(type, TBind.TBind):
        new_sub = {k: sub[k] for k in sub if k != type.variable}
        return TBind.TBind(type.variable, substitute(type.body, new_sub))
    return TypeError('not a type')


def update(type, env, sub):
    for k in env:
        env[k] = substitute(env[k], sub)
    bounds = {v for v in env.values() if isinstance(v, TVar.TVar)}
    return generalize(substitute(specialize(type), sub), bounds)


def free_vars(type, bound=None):
    if isinstance(type, TVar.TVar):
        return {type} if bound is None or type not in bound else set()
    if isinstance(type, TOp.TOp):
        return {v for a in type.args for v in free_vars(a, bound)}
    if isinstance(type, TBind.TBind):
        return free_vars(type.body, bound).difference({type.variable})
    return TypeError('not a type')


def alpha(t1, t2, sub=None):
    sub = {} if sub is None else sub
    if isinstance(t1, TVar.TVar) and isinstance(t2, TVar.TVar):
        return sub if t2 == substitute(t1, sub) else None
    elif (isinstance(t1, TOp.TOp) and isinstance(t2, TOp.TOp) and
          t1.head == t2.head and len(t1.args) == len(t2.args)):
        for st1, st2 in zip(t1.args, t2.args):
            sub = alpha(st1, st2, sub)
            if sub is None:
                return None
        return sub
    elif (isinstance(t1, TBind.TBind) and isinstance(t2, TBind.TBind) and
          t1.variable not in sub):
        sub[t1.variable] = t2.variable
        return alpha(t1.body, t2.body, sub)

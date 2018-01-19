import itertools
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind


def multi_argument_function(arg_types, result=None):
    f_type = TVar.TVar() if result is None else result
    for arg in reversed(arg_types):
        f_type = TOp.TOp('->', [arg, f_type])
    return f_type


def function(arg1, arg2):
    return TOp.TOp('->', [arg1, arg2])


def is_function(target_type):
    try:
        return target_type.head == '->' and len(target_type.args) == 2
    except AttributeError:
        return False


def result_type(target_type, final=True):
    if is_function(target_type):
        f_type = target_type
        while is_function(f_type):
            f_type = f_type.args[1]
        return f_type
    raise ValueError('not a function {!r}'.format(target_type))


def generalize(target_type, bound=None):
    the_type = target_type
    for v in free_vars(target_type, bound):
        the_type = TBind.TBind(v, the_type)
    return the_type


def specialize_top(target_type, env=None):
    if env is None:
        env = {}
    if isinstance(target_type, TBind.TBind):
        return specialize(target_type, env)
    return target_type


def specialize(target_type, env=None):
    try:  # TBind
        if target_type.variable not in env:
            env[target_type.variable] = TVar.TVar()
        return specialize(target_type.body, env)
    except AttributeError:
        pass

    try:  # TOp
        return TOp.TOp(target_type.head,
                       [specialize(arg, env) for arg in target_type.args])
    except AttributeError:
        return env.get(target_type, target_type)


def substitute(the_type, sub):
    try:
        if the_type.args == []:
            return the_type
        return TOp.TOp(the_type.head,
                       [substitute(arg, sub) for arg in the_type.args])
    except AttributeError:
        pass

    try:
        var = the_type.variable
        sub2 = sub.copy()
        sub2.pop(var, None)
        return TBind.TBind(var, substitute(the_type.body, sub2))
    except AttributeError:
        return sub.get(the_type, the_type)


def update(target_type, env, sub):
    # hard-coded variable substitution here saves time
    fvs = {v for x in free_vars_in_env(env) for v in free_vars(sub.get(x, x))}
    return generalize(substitute(specialize_top(target_type), sub), fvs)


def update2(target_type, sub):
    return substitute(specialize_top(target_type), sub)


def free_vars_in_env(env):
        return set(itertools.chain(*[free_vars(v) for v in env.values()]))


def free_vars(type, bound=None):
    try:
        return set(itertools.chain(*[free_vars(a, bound) for a in type.args]))
    except AttributeError:
        pass

    try:
        return free_vars(type.body, bound).difference({type.variable})
    except AttributeError:
        return {type} if bound is None or type not in bound else set()


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

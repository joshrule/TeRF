import TeRF.Types.Application as A
import TeRF.Types.Variable as V
import TeRF.Types.Term as T


def cache_decorator(name):
    def decorator(f):
        def wrapper(thing):
            try:
                return thing._cache[name]
            except KeyError:
                thing._cache[name] = f(thing)
            return thing._cache[name]
        return wrapper
    return decorator


def term_decorator(f):
    def wrapper(term, *args, **kwargs):
        if isinstance(term, T.Term):
            return f(term, *args, **kwargs)
        raise TypeError('not a term: {!r}'.format(term))
    return wrapper


@cache_decorator('atoms')
@term_decorator
def atoms(term):
    try:
        return {term.head} | {a for arg in term.args for a in atoms(arg)}
    except AttributeError:
        return {term}


@cache_decorator('operators')
@term_decorator
def operators(term):
    return {o for o in atoms(term) if hasattr(o, 'arity')}


@cache_decorator('variables')
@term_decorator
def variables(term):
    return {o for o in atoms(term) if not hasattr(o, 'arity')}


@cache_decorator('subterms')
@term_decorator
def places(term):
    try:
        return [[]] + [[i] + place
                       for i, arg in enumerate(term.args)
                       for place in places(arg)]
    except AttributeError:
        return [[]]


@term_decorator
def subterms(term):
    yield term
    try:
        for arg in term.args:
            for subterm in subterms(arg):
                yield subterm
    except AttributeError:
        pass


@term_decorator
def subterm(term, place):
    if len(place) == 0:
        return term
    elif isinstance(term, V.Variable):
        raise ValueError('subterm: variables are atomic')
    try:
        return subterm(term.args[place[0]], place[1:])
    except IndexError:
        raise ValueError('place: invalid place')


@term_decorator
def replace(term, place, subterm):
    if len(place) == 0:
        return subterm
    elif isinstance(term, V.Variable):
        raise ValueError('replace: variables are atomic')
    args = term.args[:]
    args[place[0]] = replace(args[place[0]], place[1:], subterm)
    return A.Application(term.head, args)


def rename_variables(term):
    for i, v in enumerate(variables(term)):
        v.name = 'v' + str(i)
    return term


def to_string(term, verbose=0):
    def list_terms(xs):
        if xs.head.name == 'nil' and xs.head.arity == 0:
            return []
        elif xs.head.name == '.':
            return [xs.args[0].args[1]] + list_terms(xs.args[1])
        elif xs.head.name == 'cons' and xs.head.arity == 2:
            return [xs.args[0]] + list_terms(xs.args[1])

    def print_list():
        items = [to_string(t, verbose) for t in list_terms(term)]
        return '[' + ', '.join(items) + ']'

    def number_value(n):
        try:
            return 1 + number_value(n.args[0])
        except IndexError:
            return 0

    def print_number():
        return str(number_value(term))

    if isinstance(term, V.Variable):
        return str(term)
    elif isinstance(term, A.Application):
        if is_list(term):
            return print_list()
        if is_number(term):
            return print_number()
        if term.head.name == '.' and term.head.arity == 2:
            if verbose == 0:
                return to_string(term.args[0], 0) + \
                    ' ' + to_string(term.args[1], 1)
            elif verbose == 1:
                return '(' + to_string(term.args[0], 0) + \
                    ' ' + to_string(term.args[1], 1) + ')'
            else:
                return '(' + to_string(term.args[0], 2) + \
                    ' ' + to_string(term.args[1], 2) + ')'
        args = '[{}]'.format(' '.join(to_string(a, 1) for a in term.args)) \
               if term.args else ''
        return str(term.head) + args
    raise TypeError('not a term')


def is_list(term):
    """assumes we're using cons/0 to encode lists"""
    try:
        return (term.head.name == '.' and
                term.head.arity == 2 and
                term.args[0].head.name == '.' and
                term.args[0].head.arity == 2 and
                term.args[0].args[0].head.name == 'cons' and
                term.args[0].args[0].head.arity == 0 and
                is_list(term.args[1])) or \
               (term.head.name == 'nil' and
                term.head.arity == 0) or \
               (term.head.name == 'cons' and
                term.head.arity == 2 and
                is_list(term.args[1]))
    except AttributeError:
        return False


def is_number(term):
    """assumes we're using S/1 to encode numbers"""
    try:
        return (term.head.name == 's' and
                term.head.arity == 1 and
                is_number(term.args[0])) or \
               (term.head.name == '0' and
                term.head.arity == 0)
    except AttributeError:
        return False


def same_structure(t1, t2, env):
    if isinstance(t1, A.App) and isinstance(t2, A.App) and t1.head == t2.head:
        for (b1, b2) in zip(t1.args, t2.args):
            env = same_structure(b1, b2, env)
            if env is None:
                break
        return env
    if isinstance(t1, V.Var) and isinstance(t2, V.Var):
        try:
            if env[t1] == t2:
                return env
            return None
        except KeyError:
            if t2 not in env.values():
                env[t1] = t2
                return env
            return None

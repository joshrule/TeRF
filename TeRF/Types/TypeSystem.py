import TeRF.Types.Variable as V
import TeRF.Types.Application as A


class TypeVariable(object):
    next_id = 0

    def __init__(self):
        self.id = TypeVariable.next_id
        TypeVariable.next_id += 1

    def __str__(self):
        return 'v' + str(self.id)


class TypeOperator(object):
    def __init__(self, name, types):
        self.name = name
        self.types = types

    def __str__(self):
        if len(self.types) == 0:
            addendum = ''
        else:
            addendum = '[' + ', '.join(str(t) for t in self.types) + ']'
        return str(self.name) + addendum


class Function(TypeOperator):
    def __init__(self, alpha_type, beta_type):
        super(Function, self).__init__('->', [alpha_type, beta_type])

    def __str__(self):
        return '(' + str(self.types[0]) + ' -> ' + str(self.types[1]) + ')'


class TypeBinding(object):
    def __init__(self, bound_variable, type):
        self.bound_variable = bound_variable
        self.type = type

    def __str__(self):
        return '()' + str(self.bound_variable) + '.' + str(self.type)


class TypeSystem(object):
    def __init__(self, env=None):
        self.default_env = {} if env is None else env
        self.typings = {}

    def type(self, term, env=None):
        if env is None:
            the_env = self.default_env.copy()
        else:
            the_env = self.default_env.copy()
            the_env.update(env)

        if term in self.typings:
            return self.typings[term]

        if isinstance(term, V.Variable):
            the_type = generalize(instantiate(the_env[term]), env=the_env)
            self.typings[term] = the_type
            return the_type

        elif isinstance(term, A.Application):
            head_type = instantiate(the_env[term.head])
            body_types = [instantiate(self.type(t, env=the_env.copy()))
                          for t in term.body]
            constraints, final_type = gather_constraints(head_type, body_types)
            substitution = unify(constraints)
            the_type = generalize(substitute(final_type, substitution),
                                  env=the_env)
            self.typings[term] = the_type
            return the_type

        else:
            raise ValueError('type: can only type terms')


def generalize(type, env):
    fvs = free_vars(type, env=env)
    the_type = type
    for v in fvs:
        the_type = TypeBinding(v, the_type)
    return the_type


def instantiate(type):
    mappings = {}

    def instrec(t):
        if isinstance(t, TypeVariable):
            try:
                return mappings[t]
            except KeyError:
                return t
        elif isinstance(t, TypeOperator):
            if isinstance(t, Function):
                return Function(instrec(t.types[0]), instrec(t.types[1]))
            return TypeOperator(t.name, [instrec(x) for x in t.types])
        elif isinstance(t, TypeBinding):
            if t.bound_variable not in mappings:
                mappings[t.bound_variable] = TypeVariable()
            return instrec(t.type)

    return instrec(type)


def gather_constraints(the_type, types):
    cs = set()
    final_type = {the_type}

    def gcrec(t, ts):
        if len(ts) == 0:
            return
        elif isinstance(t, Function):
            cs.add((t.types[0], ts[0]))
            final_type.pop()
            final_type.add(t.types[1])
            gcrec(t.types[1], ts[1:])
        else:
            raise ValueError('gather_constraints: imbalanced constraints')

    gcrec(the_type, types)
    return cs, final_type.pop()


def unify(cs):
    if len(cs) == 0:
        return {}
    else:
        (s, t) = cs.pop()
        if s == t:
            return unify(cs)
        elif isinstance(s, TypeVariable) and s not in free_vars(t):
            return compose(unify(substitute_constraints(cs,
                                                        {s: t})),
                           {s: t})
        elif isinstance(t, TypeVariable) and t not in free_vars(s):
            return compose(unify(substitute_constraints(cs,
                                                        {t: s})),
                           {t: s})
        elif (isinstance(s, TypeOperator) and
              isinstance(t, TypeOperator) and
              s.name == t.name and
              len(s.types) == len(t.types)):
            cs |= {(st, tt) for st, tt in zip(s.types, t.types)}
            return unify(cs)
        else:
            return None


def free_vars(type, env=None):
    if isinstance(type, TypeVariable):
        if env is None or type not in env.values():
            return {type}
        return set()
    elif isinstance(type, TypeOperator):
        return {v for t in type.types for v in free_vars(t)}
    elif isinstance(type, TypeBinding):
        return free_vars(type).difference({type.bound_variable})
    else:
        raise ValueError('free_vars: bad type')


def substitute(type, substitution):
    if isinstance(type, TypeVariable):
        if type in substitution:
            return substitution[type]
        return type
    elif isinstance(type, Function):
        return Function(substitute(type.types[0], substitution),
                        substitute(type.types[1], substitution))
    elif isinstance(type, TypeOperator):
        return TypeOperator(type.name, [substitute(t, substitution)
                                        for t in type.types])
    elif isinstance(type, TypeBinding):
        # TODO: do we need to do any sort of name checking here?
        return TypeBinding(type.bound_variable,
                           substitute(type.type, substitution))
    pass


def substitute_constraints(constraints, substitution):
    return {(substitute(k, substitution), substitute(v, substitution))
            for k, v in constraints}


def compose(sub1, sub2):
    result = sub1.copy()
    result.update({k: substitute(sub2[k], sub1) for k in sub2})
    return result


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg
    import time

    # setup a few helper types
    LIST = TypeOperator('LIST', [])
    NAT = TypeOperator('NAT', [])
    vA = TypeVariable()
    vB = TypeVariable()
    vC = TypeVariable()
    vD = TypeVariable()
    vE = TypeVariable()
    vF = TypeVariable()
    vG = TypeVariable()
    vH = TypeVariable()
    x = V.Variable('x')

    class List(TypeOperator):
        def __init__(self, alpha_type):
            super(List, self).__init__('LIST', [alpha_type])

    class Pair(TypeOperator):
        def __init__(self, alpha_type, beta_type):
            super(Pair, self).__init__('PAIR', [alpha_type, beta_type])

    # create a type system
    types = {tg.NIL: TypeBinding(vC, List(vC)),
             tg.ZERO: NAT,
             tg.ONE: NAT,
             tg.TWO: NAT,
             tg.THREE: NAT,
             tg.CONS: TypeBinding(vD,
                                  Function(vD,
                                           Function(List(vD),
                                                    List(vD)))),
             tg.DOT: TypeBinding(vA, TypeBinding(vB,
                                                 Function(Function(vA, vB),
                                                          Function(vA, vB)))),
             tg.HEAD: TypeBinding(vE, Function(List(vE), vE)),
             tg.ID: TypeBinding(vF, Function(vF, vF)),
             tg.PAIR: TypeBinding(vG,
                                  TypeBinding(vH,
                                              Function(vG,
                                                       Function(vH,
                                                                Pair(vG,
                                                                     vH))))),
             x: TypeVariable()}

    tsys = TypeSystem(env=types.copy())

    # type some terms
    t1 = tg.g(tg.j(tg.PAIR,
                   tg.j(tg.ID, tg.k(tg.h(tg.CONS, tg.ONE), tg.NIL))),
              tg.h(tg.ID, tg.ZERO))

    for term in [tg.f(tg.NIL),
                 tg.f(tg.CONS),
                 tg.h(tg.HEAD, tg.NIL),
                 tg.h(tg.CONS, tg.ONE),
                 tg.j(tg.HEAD, tg.g(tg.j(tg.CONS, tg.h(tg.HEAD, tg.NIL)),
                                    tg.g(tg.j(tg.CONS, tg.f(tg.TWO)),
                                         tg.f(tg.NIL)))),
                 tg.k(tg.j(tg.CONS, x), tg.NIL),
                 tg.k(tg.h(tg.PAIR, tg.NIL), tg.ZERO),
                 tg.g(tg.j(tg.PAIR,
                           tg.h(tg.ID, tg.NIL)),
                      tg.h(tg.ID, tg.ZERO)),
                 t1,
                 t1,
                 t1,
                 tg.f(tg.PAIR)]:
        print 'term:', term.to_string()
        start = time.time()
        type = tsys.type(term)
        stop = time.time()
        print 'type:', type
        print 'time:', 1e6*(stop-start)/float(len(term))
        print

    for st in term.subterms:
        print st.to_string(), tsys.type(st)

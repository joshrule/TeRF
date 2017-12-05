"""Much thanks to https://github.com/rob-smallshire/hindley-milner-python/"""

import TeRF.Miscellaneous as misc
import TeRF.Types.Variable as V
import TeRF.Types.Application as A
import numpy as np


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
        return str(self.name) + misc.iter2ListStr(self.types, empty='')


class Function(TypeOperator):
    def __init__(self, alpha_type, beta_type):
        super(Function, self).__init__('->', [alpha_type, beta_type])

    def __str__(self):
        return '(' + str(self.types[0]) + ' -> ' + str(self.types[1]) + ')'


class TypeBinding(object):
    def __init__(self, bound, type):
        self.bound = bound
        self.type = type

    def __str__(self):
        return '()' + str(self.bound) + '.' + str(self.type)


class TypeSystem(object):
    def __init__(self, env=None):
        self.default_env = {} if env is None else env
        self.typings = {}

    def make_env(self, env=None):
        the_env = self.default_env.copy()
        if env is not None:
            the_env.update(env)
        return the_env

    def type(self, term, env, sub):
        if isinstance(term, V.Variable):
            return update(term, env, sub)
        elif isinstance(term, A.Application) and term.head.arity == 0:
            return update(term.head, env, sub)
        elif isinstance(term, A.Application):
            head_type = substitute(specialize(env[term.head]), sub)
            result_type = TypeVariable()
            body_type = functify([specialize(self.type(t, env, sub))
                                  for t in term.body],
                                 result=result_type)
            try:
                compose(sub, unify({(head_type, body_type)}))
            except TypeError:
                raise ValueError('untypable: ' + term.to_string())
            return generalize(substitute(result_type, sub),
                              substitute_context(env, sub))
        raise ValueError('can only type terms: ' + str(term))

    def type_rule(self, rule, env, sub):
        lhs_type = specialize(self.type(rule.lhs, env, sub))
        rhs_types = [specialize(self.type(rhs, env.copy(), sub))
                     for rhs in rule.rhs]
        new_sub = unify({(lhs_type, rhs_type) for rhs_type in rhs_types})
        if new_sub is not None:
            return generalize(substitute(lhs_type, new_sub),
                              substitute_context(env, compose(new_sub, sub)))
        raise ValueError('untypable: ' + str(rule))

    def sample_term(self, type, env=None):
        the_env = self.default_env.copy()
        if env is not None:
            the_env.update(env)

        options = []
        for atom in the_env:
            term_env = the_env.copy()
            term = make_dummy_term(atom, term_env)
            sub = construct_substitution(term, type, self, term_env)
            if sub is not None:
                options.append((term, sub, term_env))

        term, sub, term_env = options[np.random.choice(len(options))]
        if isinstance(term, V.Variable):
            return term
        subterm_types = [substitute(term_env[v], sub) for v in term.body]
        subterms = []
        constraints = set()
        for subterm_type in subterm_types:
            specialized_type = substitute(subterm_type, unify(constraints))
            subterm = self.sample_term(specialized_type, env=the_env)
            subterms.append(subterm)
            constraints.add((subterm_type,
                             specialize(self.type(subterm, env=the_env))))
        return A.Application(term.head, subterms)

    def log_p_term(self, term, type, env=None):
        the_env = self.default_env.copy()
        if env is not None:
            the_env.update(env)

        options = []
        matches = []
        for atom in the_env:
            term_env = the_env.copy()
            dummy_term = make_dummy_term(atom, term_env)
            sub = construct_substitution(dummy_term, type, self, term_env)
            if sub is not None:
                options.append((dummy_term, sub, term_env))
            if term.head == atom:
                matches.append((dummy_term, sub, term_env))
        if len(matches) > 1:
            raise ValueError('log_p_term: too many options')

        log_ps = [misc.logNof(options, n=len(matches))]

        d_term, sub, term_env = matches[np.random.choice(len(matches))]

        if isinstance(d_term, V.Variable):
            return log_ps[0]

        subterm_types = [substitute(term_env[v], sub) for v in d_term.body]
        constraints = set()
        for subterm, subterm_type in zip(term.body, subterm_types):
            specialized_type = substitute(subterm_type, unify(constraints))
            log_ps.append(self.log_p_term(subterm,
                                          specialized_type,
                                          env=the_env))
            constraints.add((subterm_type,
                             specialize(self.type(subterm, env=the_env))))
        return sum(log_ps)


def update(atom, env, sub):
    return generalize(substitute(specialize(env[atom]),
                                 sub),
                      substitute_context(env, sub))


def make_dummy_term(atom, env):
    if isinstance(atom, V.Variable):
        term = atom
    else:
        term = A.Application(atom, [V.Variable() for _ in xrange(atom.arity)])
        env.update({v: TypeVariable() for v in term.body})

    return term


def construct_substitution(term, target_type, typesystem, env):
    if isinstance(term, V.Variable):
        result_type = generalize(specialize(env[term]), env=env)
        constraints = set()

    elif isinstance(term, A.Application):
        head_type = specialize(env[term.head])
        body_types = [specialize(typesystem.type(t, env=env.copy()))
                      for t in term.body]
        result_type = TypeVariable()
        constraints = {(head_type, functify(body_types, result=result_type))}
    substitution = unify(constraints | {(result_type, target_type)})
    return substitution


def generalize(type, env):
    fvs = free_vars(type, env=env)
    the_type = type
    for v in fvs:
        the_type = TypeBinding(v, the_type)
    return the_type


def specialize(type):
    mappings = {}

    def specrec(t):
        if isinstance(t, TypeVariable):
            try:
                return mappings[t]
            except KeyError:
                return t
        elif isinstance(t, TypeOperator):
            if isinstance(t, Function):
                return Function(specrec(t.types[0]), specrec(t.types[1]))
            return TypeOperator(t.name, [specrec(x) for x in t.types])
        elif isinstance(t, TypeBinding):
            if t.bound not in mappings:
                mappings[t.bound] = TypeVariable()
            return specrec(t.type)

    return specrec(type)


def functify(arg_types, result=None):
    f_type = TypeVariable() if result is None else result
    while len(arg_types) > 0:
        f_type = Function(arg_types.pop(), f_type)
    return f_type


def unify(cs):
    try:
        (s, t) = cs.pop()
    except KeyError:
        return {}

    if s == t:
        return unify(cs)
    elif isinstance(s, TypeVariable) and s not in free_vars(t):
        partial = unify(substitute_constraints(cs, {s: t}))
        compose(partial, {s: t})
        return partial
    elif isinstance(t, TypeVariable) and t not in free_vars(s):
        partial = unify(substitute_constraints(cs, {t: s}))
        compose(partial, {t: s})
        return partial
    elif (isinstance(s, TypeOperator) and isinstance(t, TypeOperator) and
          s.name == t.name and len(s.types) == len(t.types)):
        return unify(cs | {(st, tt) for st, tt in zip(s.types, t.types)})
    else:
        return None


def free_vars(type, env=None):
    if isinstance(type, TypeVariable):
        return {type} if env is None or type not in env.values() else set()
    elif isinstance(type, TypeOperator):
        return {v for t in type.types for v in free_vars(t, env=env)}
    elif isinstance(type, TypeBinding):
        return free_vars(type, env=env).difference({type.bound})
    raise ValueError('free_vars: bad type')


def substitute(type, substitution):
    if isinstance(type, TypeVariable):
        return substitution[type] if type in substitution else type
    elif isinstance(type, Function):
        return Function(substitute(type.types[0], substitution),
                        substitute(type.types[1], substitution))
    elif isinstance(type, TypeOperator):
        return TypeOperator(type.name, [substitute(t, substitution)
                                        for t in type.types])
    elif isinstance(type, TypeBinding):
        return TypeBinding(type.bound, substitute(type.type, substitution))
    raise ValueError('free_vars: bad type')


def substitute_context(context, substitution):
    return {k: substitute(v, substitution) for k, v in context.iteritems()}


def substitute_constraints(constraints, substitution):
    return {(substitute(k, substitution), substitute(v, substitution))
            for k, v in constraints}


def compose(sub1, sub2):
    if sub1 is not None:
        sub1.update({k: substitute(sub2[k], sub1) for k in sub2})
        return sub1


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg
    import TeRF.Types.Rule as R
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
    vI = TypeVariable()
    x = V.Variable('x')
    y = V.Variable('y')
    z = V.Variable('z')

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
             x: vI,
             y: TypeVariable(),
             z: vI}

    tsys = TypeSystem(env=types.copy())

    # type some terms
    t1 = tg.g(tg.j(tg.PAIR,
                   tg.j(tg.ID, tg.k(tg.h(tg.CONS, tg.ONE), tg.NIL))),
              tg.h(tg.ID, tg.ZERO))

    print 'let\'s type some terms'
    for term in [x,
                 tg.f(tg.NIL),
                 tg.f(tg.CONS),
                 tg.h(tg.HEAD, tg.NIL),
                 tg.h(tg.CONS, tg.ONE),
                 tg.j(tg.CONS, x),
                 tg.j(tg.CONS, x),
                 tg.g(tg.j(tg.CONS, x), x),
                 tg.g(tg.h(tg.CONS, tg.ONE), x),
                 tg.k(tg.h(tg.CONS, tg.ONE), tg.TWO),
                 tg.g(tg.h(tg.CONS, tg.ONE), tg.k(tg.j(tg.CONS, x),
                                                  tg.NIL)),
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
                 tg.f(tg.PAIR),
                 tg.g(tg.j(tg.CONS, x), z),
                 tg.g(tg.j(tg.CONS, x), y),
                 ]:
        print 'term:', term.to_string()
        start = time.time()
        try:
            type = tsys.type(term, tsys.make_env(None), {})
        except ValueError:
            type = 'FAIL'
        stop = time.time()
        print 'type:', type
        print 'time:', 1e6*(stop-start)/float(len(term))
        print

    print 'showing how subterms can easily be typed'
    env = tsys.make_env(None)
    sub = {}
    for st in term.subterms:
        print st.to_string(), tsys.type(st, env, sub)

    print '\n', 'rules can also be typed'
    rules = [R.Rule(tg.h(tg.HEAD, tg.NIL), [tg.f(tg.NIL), tg.k(tg.h(tg.CONS,
                                                                    tg.TWO),
                                                               tg.NIL)]),
             R.Rule(tg.f(tg.PAIR), tg.f(tg.ID))]
    for rule in rules:
        print 'rule:', rule
        try:
            type = tsys.type_rule(rule, tsys.make_env(None), {})
            print 'type:', type
        except ValueError:
            print 'type: FAIL'
        print

            #    print
#    for atom in types:
#        the_env = tsys.default_env.copy()
#        term = make_dummy_term(atom, the_env)
#        sub = construct_substitution(term, NAT, tsys, the_env)
#        print 'atom:', atom
#        print 'term:', term
#        if sub is not None:
#            print 'sub:'
#            for k, v in sub.iteritems():
#                print '   ', k, ':', v
#
#    print
#    del tsys.default_env[x]
#    del tsys.default_env[tg.ID]
#    del tsys.default_env[tg.PAIR]
#    for _ in xrange(10):
#        term = tsys.sample_term(NAT)
#        print 'term:'
#        print '   ', term.to_string()
#        print '   ', tsys.type(term)
#        log_p = tsys.log_p_term(term, NAT)
#        print '   ', log_p, 1./np.exp(log_p)

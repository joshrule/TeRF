"""
TODO: Neither of these routines manage variables at all
"""

import numpy as np
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as App
import TeRF.Types.Rule as Rule
import TeRF.Types.Variable as Var
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.TypeUnify as tu


def sample_rule(typesystem, target_type, env):
    return Rule.Rule(sample_term(typesystem, target_type, env),
                     sample_term(typesystem, target_type, env))


def sample_term(target_type, env, sub, max_depth, depth=0):
    """samples a term with progress bounds and backtracking"""
    if depth > max_depth:
        raise ValueError('sample_term: exceeded max depth')
    options = list_options(target_type, env, sub)
    while len(options) > 0:
        choice = np.random.choice(len(options))
        term, sub, term_env = options[choice]
        del options[choice]
        try:
            if isinstance(term, Var.Var):
                return term
            subterms = []
            constraints = set()
            for i, v in enumerate(term.body):
                new_sub = tu.compose(tu.unify(constraints.copy()), sub)
                subtype = ty.specialize(tc.typecheck(v, term_env, new_sub))
                new_depth = (depth+1)*(i == 0)
                subterm = sample_term(subtype, env, sub, max_depth,
                                      depth=new_depth)
                subterms.append(subterm)
                final_type = ty.specialize(tc.typecheck(subterm, env, sub))
                constraints.add((subtype, final_type))
            return App.App(term.head, subterms)
        except ValueError:
            pass
    raise ValueError('sample_term: options exhausted')


def list_options(type, env, sub):
    options = []
    for atom in env:
        a_env = env.copy()
        a_sub = sub.copy()
        term = make_dummy_term(atom, a_env)
        sub = construct_substitution(term, type, a_env, a_sub)
        if sub is not None:
            options.append((term, sub, a_env))
    return options


def log_p_term(term, type, env, sub, max_depth, depth=0):
    if depth > max_depth:
        return -np.inf

    options = list_options(type, env, sub)
    matches = [o for o in options if o[0].head == term.head]
    if len(matches) > 1:
        raise ValueError('log_p_term: bad context')

    log_p = misc.logNof(options, n=len(matches))

    if log_p == -np.inf:
        return log_p

    d_term, sub, term_env = matches[0]

    if isinstance(d_term, Var.Var):
        return log_p

    log_ps = [log_p]
    constraints = set()
    for i, (subterm, v) in enumerate(zip(term.body, d_term.body)):
        new_sub = tu.compose(tu.unify(constraints.copy()), sub)
        subtype = ty.specialize(tc.typecheck(v, term_env, new_sub))
        new_depth = (depth+1)*(i == 0)
        log_ps.append(log_p_term(subterm, subtype, env, sub, max_depth,
                                 depth=new_depth))
        final_type = ty.specialize(tc.typecheck(subterm, env, sub))
        constraints.add((subtype, final_type))
    log_p = sum(log_ps)
    return sum(log_ps)


def make_dummy_term(atom, env):
    if isinstance(atom, Var.Var):
        term = atom
    else:
        term = App.App(atom, [Var.Var() for _ in xrange(atom.arity)])
        env.update({v: TVar.TVar() for v in term.body})
    return term


def construct_substitution(term, target_type, env, sub):
    if isinstance(term, Var.Var):
        result_type = tu.update(term, env, sub)
        constraints = set()

    elif isinstance(term, App.App):
        head_type = tu.specialize(tu.update(term.head, env, sub))
        body_types = [tu.specialize(tc.typecheck(t, env.copy(), sub))
                      for t in term.body]
        result_type = TVar.TVar()
        constraints = {(head_type,
                        tu.multi_argument_function(body_types,
                                                   result=result_type))}
    return tu.compose(tu.unify(constraints |
                               {(result_type, ty.specialize(target_type))}),
                      sub)

from copy import copy
from numpy import log, exp
from numpy.random import binomial, choice
from scipy.misc import logsumexp
from TRS import Variable, Application, Term, TRSError, Atom
from TRS import App, Var, Op
from Miscellaneous import branch_assignment, all_branch_assignments


class GenerationError(Exception):
    pass


def invalid_signature(signature):
    return not (signature and all([isinstance(s, Atom) for s in signature]))


def sample_term(signature):
    """
    sample a TRS term given a TRS signature

    Args:
      signature: an iterable containing TRS Operators and Variables
    Returns:
      a TRS term sampled from the grammar defined by signature
    Raises:
      GenerationError: raised when the signature is invalid
    """
    if invalid_signature(signature):
        raise GenerationError('sample_term: invalid signature')

    head = choice(list(signature))
    try:
        body = [sample_term(signature) for operand in range(head.arity)]
        return Application(head, body)
    except AttributeError:  # it's a variable
        return head


def log_p(term, signature):
    """
    compute the probability of sampling a term given a signature

    Args:
      term: a TRS term
      signature: an iterable containing TRS Operators and Variables
    Returns:
      a float representing log(p(term | signature))
    """
    if invalid_signature(signature) or not isinstance(term, Term):
        return log(0)

    if (isinstance(term, Var) and term in signature) or  \
       (isinstance(term, App) and term.head in signature):
        p_head = -log(len(signature))
        try:
            p_body = [log_p(operand, signature) for operand in term.body]
            return p_head + sum(p_body)
        except AttributeError:
            return p_head
    else:
        return log(0)


def sample_term_t(signature, term, p_r):
    """
    generate a term conditioned on an existing term

    Args:
      signature: an iterable of TRS Operators and Variables
      term: a TRS term
      p_r: a float giving the node-wise probability of regeneration
    Returns:
      a TRS term
    Raises:
      GenerationError: raised when the signature is invalid or no term is
          provided on which to condition.
    """
    if invalid_signature(signature):
        raise GenerationError('sample_term_t: invalid signature')
    elif not isinstance(term, Term):
        raise GenerationError('sample_term_t: not given a term!')
    elif binomial(1, p_r):
        return sample_term(signature)
    try:
        new_body = [sample_term_t(signature, part, p_r) for part in term.body]
        return Application(term.head, new_body)
    except AttributeError:
        return copy(term)


def log_p_t(new, signature, old, p_r):
    """
    compute the probability of sampling a term given a signature and term

    Args:
      new: a TRS term
      signature: an iterable of TRS Operators and Variables
      old: the TRS term upon which new was conditioned during sampling
      p_r: a float giving the node-wise probability of regeneration
    Returns:
      a float representing log(p(new | signature, old))
"""
    if invalid_signature(signature) or not isinstance(old, Term):
        return log(0)
    elif isinstance(old, Var) and old == new and old in signature:
        return logsumexp([log(1-p_r), log(p_r) - log(len(signature))])
    elif (isinstance(old, App) and isinstance(new, App) and
          old.head == new.head and old.head in signature):
        log_ps = [log_p_t(n, signature, o, p_r)
                  for n, o in zip(new.body, old.body)]
        return logsumexp([log(1-p_r) + sum(log_ps),
                          log(p_r) + log_p(new, signature)])
    elif isinstance(new, Var) and new in signature:
        return log(p_r) - log(len(signature))
    elif isinstance(new, App) and new.head in signature:
        return log(p_r) + log_p(new, signature)
    else:
        return log(0)


def filter_heads(signature, constraints):
    if len(constraints) == 0:
        return list(signature)
    if len(constraints) == 1:
        return [s for s in signature
                if s in constraints or (isinstance(s, Op) and s.arity > 0)]
    else:  # 2+ constraints
        return [s for s in signature if isinstance(s, Op) and s.arity > 1]


def sample_term_c(signature, constraints):
    """
    generate a term conditioned on a signature a set of required symbols

    Args:
      signature: an iterable of TRS Operators and Variables
      constraints: an iterable subset of signature that must appear in term
    Returns:
      a TRS term
    Raises:
      GenerationError: raised when the signature or constraints are invalid
    """
    if invalid_signature(signature):
        raise GenerationError('sample_term_c: invalid signature')
    elif not set(signature) >= set(constraints):
        raise GenerationError('sample_term_c: invalid constraints')

    head = choice(filter_heads(signature, constraints))

    try:
        body_constraints = branch_assignment(set(constraints)-{head},
                                             range(head.arity))
        body = [sample_term_c(signature, cs) for cs in body_constraints]
        return App(head, body)
    except AttributeError:
        return head


def log_p_c(term, signature, constraints):
    """
    compute the probability of sampling a term given a signature and term

    Args:
      term: a TRS term
      signature: an iterable of TRS Operators and Variables
      constraints: an iterable subset of signature that must appear in term
    Returns:
      a float representing log(p(term | signature, constraints))
    """
    if invalid_signature(signature) or not signature >= constraints:
        return log(0)
    
    heads = filter_heads(signature, constraints)
    head = term.head if isinstance(term, App) else term
    p_head = -log(len(heads)) if head in heads else log(0)

    if isinstance(term, Var):
        p_body = log(1)
    elif isinstance(term, App):
        asns, p_asns = all_branch_assignments(set(constraints)-{head},
                                              range(head.arity))
        ps_body = [sum([log_p_c(b, signature, cs)
                        for b, cs in zip(term.body, asn)])
                   for asn in asns]
        if ps_body:
            p_body = logsumexp([sum(ps) for ps in zip(p_asns, ps_body)])
        else:
            p_body = log(0)
    else:
        p_body = log(0)
    return (p_head + p_body)


def sample_term_tc(signature, term, p_r, constraints):
    """
    generate a term conditioned on a signature a set of required symbols

    Args:
      signature: an iterable of TRS Operators and Variables
      term: a TRS term
      p_r: a float giving the node-wise probability of regeneration
      constraints: an iterable subset of signature that must appear in term
    Returns:
      a TRS term
    Raises:
      GenerationError: raised when the signature or constraints are invalid
    """
    if invalid_signature(signature):
        raise GenerationError('sample_term_tc: invalid signature')
    elif not isinstance(term, Term):
        raise GenerationError('sample_term_tc: not given a term!')
    elif not set(signature) >= set(constraints):
        raise GenerationError('sample_term_tc: invalid constraints')
    elif (binomial(1, p_r)) or \
         (isinstance(term, Var) and not set(constraints) <= {term}) or \
         (isinstance(term, App) and len(constraints) == 1 and
          term.head.arity < 1) or \
         (isinstance(term, App) and len(constraints) > 1 and
          term.head.arity < 2):
        return sample_term_c(signature, constraints)
    elif isinstance(term, Var):
        return copy(term)
    else:
        body_cs = branch_assignment(set(constraints)-{term.head},
                                    range(term.head.arity))
        body = [sample_term_tc(signature, part, p_r, cs)
                for part, cs in zip(term.body, body_cs)]
        return Application(term.head, body)


def log_p_tc(new, signature, old, p_r, constraints):
    """
    compute the probability of sampling a term given a signature, term, and
    required atoms

    Args:
      new: a TRS term
      signature: an iterable of TRS Operators and Variables
      old: the TRS term on which new is conditioned
      p_r: a float giving the node-wise probability of regeneration
      constraints: an iterable subset of signature that must appear in term
    Returns:
      a float representing log(p(term | signature, old, constraints))
    """
    if invalid_signature(signature) or not isinstance(new, Term) or \
       not isinstance(old, Term) or (not signature >= constraints):
        return log(0)
    else:
        if ((isinstance(old, Var) and len(constraints) > 0 and old == new) or
            (isinstance(old, App) and len(constraints) == 1 and
             old.head.arity < 1) or
            (isinstance(old, App) and len(constraints) > 1 and
             old.head.arity < 2)):  # regeneration even if flip fails
            p_no_regen = log_p_c(new, signature, constraints)
        elif isinstance(old, Variable) and old == new:
            p_no_regen = log(1)
        elif (isinstance(old, App) and isinstance(new, App) and
              old.head == new.head):
                
            asns, p_asns = all_branch_assignments(set(constraints)-{old.head},
                                                  range(old.head.arity))
            ps_body = [sum([log_p_tc(n, signature, o, p_r, cs)
                            for n, o, cs in zip(new.body, old.body, asn)])
                       for asn in asns]
            p_no_regen = logsumexp([sum(ps) for ps in zip(p_asns, ps_body)])
        else:  # no way to get there without regeneration
            p_no_regen = log(0)

        p_regen = log(p_r) + log_p_c(new, signature, constraints)
        p_no_regen += log(1-p_r)
        return logsumexp([p_regen, p_no_regen])


# # # Evaluating Terms # # #
def eval(self, term, steps=1):
    count = 0
    while count < steps:
        term, changed = self.single_step(term)
        if changed:
            count += 1
        else:
            break
    return term


def evals_to(self, t1, t2, steps=100):
    count = 0
    normal_form = False
    evals_to = False
    while (count < steps+1) and not normal_form:
        t1, changed = self.single_step(t1)
        if changed:
            count += 1
        else:
            normal_form = True
        if evals_to:
            break
        if t1 == t2:
            evals_to = True
    return count, evals_to, normal_form


def single_step(self, term, changed=False):
    if isinstance(term, Term):
        if not changed:
            for rule in [rule for rule in self.rules if rule is not None]:
                sub = unify(rule.lhs, term, type='match')
                if sub is not None:
                    return rewrite(rule.rhs, sub), True
            try:
                for idx in range(len(term.body)):
                    term.body[idx], changed = \
                        self.single_step(term.body[idx], changed)
                    if changed:
                        break
            except AttributeError:
                pass
        return term, changed
    else:
        raise TRSError('single_step: Can only evaluate terms')


def rewrite(term, sub):
    if isinstance(term, Variable):
        if term in sub:
            return sub[term]
        else:
            raise TRSError('rewrite: Variable has no definition!')
    elif isinstance(term, Application):
        return Application(term.head,
                           [rewrite(part, sub) for part in term.body])


def unify(t1, t2, env=-1, type='simple'):
    """unify two terms to produce a substitution

    t1, t2: Terms
    env: the substitution
    type: 'simple' is for unification, while 'match' is for rewriting
    """
    if env == -1:
        env = {}

    if isinstance(t1, Variable) and env is not None:
        return unify_var(t1, t2, env, type)

    elif isinstance(t2, Variable) and env is not None and type == 'simple':
        return unify_var(t2, t1, env, type)

    elif (isinstance(t1, Application) and
          isinstance(t2, Application) and
          t1.head == t2.head and
          env is not None):
        # unify each subterm
        for (st1, st2) in zip(t1.body, t2.body):
            env = unify(st1, st2, env, type)
        return env

    else:
        return None


def unify_var(t1, t2, env, type='simple'):
    if env is not None:
        if isinstance(t1, Variable):
            if t1 in env:
                unify(env[t1], t2, env, type)
            elif t2 in env:
                unify(t1, env[t2], env, type)
            else:
                if t1 == t2:
                    return env
                else:
                    env[t1] = t2
                    return env
        else:
            raise Exception('unify-var: first arg must be a variable')
    else:
        return env


if __name__ == '__main__':

    signature = {Op('S', 0),
                 Op('K', 0),
                 Op('.', 2),
                 Var('x'),
                 Var('y')}

    print 'terms'
    ts = [sample_term(signature) for _ in range(20)]
    ps = [log_p(t, signature) for t in ts]
    for t, p in zip(ts, ps):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

    print 'terms | terms'
    ts2 = [sample_term_t(signature, ts[0], 0.2) for _ in range(20)]
    ps2 = [log_p_t(t2, signature, ts[0], 0.2) for t2 in ts2]
    for t, p in zip(ts2, ps2):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

    print 'terms | constraints'
    ts3 = [sample_term_c(signature, {Op('S', 0), Op('K', 0)})
           for _ in range(5)]
    ps3 = [log_p_c(t, signature, {Op('S', 0), Op('K', 0)}) for t in ts3]
    for t, p in zip(ts3, ps3):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

    print 'terms | term, constraints'
    ts4 = [sample_term_tc(signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for _ in range(5)]
    ps4 = [log_p_tc(t, signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for t in ts4]
    for t, p in zip(ts4, ps4):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

from copy import copy
from itertools import chain, repeat, izip
from numpy import exp, argmin
from numpy.random import binomial, choice
from scipy.misc import logsumexp
from zss import distance

from TeRF.TRS import Variable, Application, TRSError
from TeRF.TRS import App, Var, Op, RR
from TeRF.Miscellaneous import gift, list_possible_gifts, log0


class GenerationError(Exception):
    pass


def terminals(signature):
    return [atom for atom in signature
            if not hasattr(atom, 'arity') or atom.arity == 0]


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
    if terminals(signature) == []:
        raise ValueError('sample_term: term cannot terminate')
    head = choice(list(signature))
    try:
        body = [sample_term(signature) for _ in repeat(None, head.arity)]
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
    if term in signature or hasattr(term, 'head') and term.head in signature:
        p_head = -log0(len(signature))
        try:
            p_body = [log_p(operand, signature) for operand in term.body]
            return p_head + sum(p_body)
        except AttributeError:
            return p_head

    return log0(0)


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
    if binomial(1, p_r):
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
    if hasattr(old, 'identity') and old == new and old in signature:
        return logsumexp([log0(1-p_r), log0(p_r) - log0(len(signature))])
    elif (hasattr(old, 'head') and hasattr(new, 'head') and
          old.head == new.head and old.head in signature):
        log_ps = [log_p_t(n, signature, o, p_r)
                  for n, o in izip(new.body, old.body)]
        return logsumexp([log0(1-p_r) + sum(log_ps),
                          log0(p_r) + log_p(new, signature)])
    elif hasattr(new, 'identity') and new in signature:
        return log0(p_r) - log0(len(signature))
    elif hasattr(new, 'head') and new.head in signature:
        return log0(p_r) + log_p(new, signature)
    else:
        return log0(0)


def filter_heads(signature, constraints):
    if len(constraints) == 0:
        return list(signature)
    if len(constraints) == 1:
        return [s for s in signature
                if s in constraints or (hasattr(s, 'arity') and s.arity > 0)]
    else:  # 2+ constraints
        return [s for s in signature if hasattr(s, 'arity') and s.arity > 1]


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
    if not set(signature) >= set(constraints):
        raise GenerationError('sample_term_c: invalid constraints')

    head = choice(filter_heads(signature, constraints))

    try:
        body_constraints = gift(set(constraints)-{head}, head.arity)
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
    if not signature >= constraints:
        return log0(0)

    heads = filter_heads(signature, constraints)
    head = term.head if hasattr(term, 'head') else term
    p_head = -log0(len(heads)) if head in heads else log0(0)

    if hasattr(term, 'identity'):
        p_body = log0(1)
    elif hasattr(term, 'head'):
        who_has_what = [[c if c in (b.variables() | b.operators()) else None
                         for c in set(constraints)-{head}]
                        for b in term.body]
        gfts = list_possible_gifts(who_has_what)
        p_gfts = -log0(len(gfts))
        ps_body = [sum([log_p_c(b, signature, cs)
                        for b, cs in izip(term.body, gft)])
                   for gft in gfts]
        if ps_body:
            p_body = logsumexp([p+p_gfts for p in ps_body])
        else:
            p_body = log0(0)
    else:
        p_body = log0(0)
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
    if not set(signature) >= set(constraints):
        raise GenerationError('sample_term_tc: invalid constraints')
    elif (binomial(1, p_r)) or \
         (hasattr(term, 'identity') and not set(constraints) <= {term}) or \
         (hasattr(term, 'head') and len(constraints) == 1 and
          term.head.arity < 1) or \
         (hasattr(term, 'head') and len(constraints) > 1 and
          term.head.arity < 2):
        return sample_term_c(signature, constraints)
    elif hasattr(term, 'identity'):
        return copy(term)
    else:
        body_cs = gift(set(constraints)-{term.head},
                       term.head.arity)
        body = [sample_term_tc(signature, part, p_r, cs)
                for part, cs in izip(term.body, body_cs)]
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
    if (not signature >= constraints):
        return log0(0)
    else:
        if ((isinstance(old, Var) and len(constraints) > 0 and old == new) or
            (isinstance(old, App) and len(constraints) == 1 and
             old.head.arity < 1) or
            (isinstance(old, App) and len(constraints) > 1 and
             old.head.arity < 2)):  # regeneration even if flip fails
            p_no_regen = log_p_c(new, signature, constraints)
        elif isinstance(old, Variable) and old == new:
            p_no_regen = log0(1)
        elif (isinstance(old, App) and isinstance(new, App) and
              old.head == new.head):
            who_has_what = [[c if c in (b.variables() | b.operators()) else None
                             for c in set(constraints)-{old.head}]
                            for b in new.body]
            gfts = list_possible_gifts(who_has_what)
            p_gfts = -log0(len(gfts))
            ps_body = [sum([log_p_tc(n, signature, o, p_r, cs)
                            for n, o, cs in izip(new.body, old.body, gft)])
                       for gft in gfts]
            if ps_body:
                p_no_regen = logsumexp([p+p_gfts for p in ps_body])
            else:
                p_no_regen = log0(0)
        else:  # no way to get there without regeneration
            p_no_regen = log0(0)

        p_regen = log0(p_r) + log_p_c(new, signature, constraints)
        p_no_regen += log0(1-p_r)
        return logsumexp([p_regen, p_no_regen])


def edit_distance(t1, t2):
    def get_cs(t):
        return [] if isinstance(t, Var) else t.body

    def insert_c(t):
        return 1

    def remove_c(t):
        return 1

    def update_c(t1, t2):
        return 0 if t1 == t2 else 1

    return distance(t1, t2, get_cs, insert_c, remove_c, update_c)


def rewrite(trs, term, steps=1):
    count = 0
    while count < steps:
        term, changed, _ = single_rewrite(trs, term)
        if changed:
            count += 1
        else:
            break
    return term


def rewrites_to(trs, t1, t2, steps=100):
    step, nf_step = 0, -1
    ts = [t1]
    while (step <= steps) and nf_step < 0:
        t, changed, _ = single_rewrite(trs, ts[-1])
        ts.append(t)
        if changed:
            step += 1
        else:
            nf_step = step
            ts = ts[:-1]
    # distances = [edit_distance(t1, tree) for tree in ts]
    distances = [int(tree != t2) for tree in ts]
    min_step = argmin(distances)
    return min_step, distances[min_step], nf_step


def single_rewrite(trs, term):
    for rule in trs.rules:
        success, sub = unify(rule.lhs, term, type='match')
        if success and sub is not {}:
            new_term = substitute(copy(rule.rhs), sub)
            return new_term, (new_term != term), True

    try:
        for idx in xrange(len(term.body)):
            part, changed, stepped = single_rewrite(trs, term.body[idx])
            if stepped:
                new_term = Application(term.head,
                                       term.body[:max(0, idx)] +
                                       [part] +
                                       term.body[max(1, idx+1):])
                return new_term, changed, True
        return term, False, False
    except AttributeError:
        return term, False, False


def substitute(term, sub):
    try:
        return Application(term.head,
                           [substitute(part, sub) for part in term.body])
    except AttributeError:
        try:
            return sub[term]
        except KeyError:
            raise TRSError('rewrite: Variable has no definition!')


class UnifyError(Exception):
    pass


def alpha_eq(t1, t2, env=None):
    if env is None:
        env = {}

    if t1 == t2:
        return True, env

    if hasattr(t1, 'identity'):
        if t1 not in env and hasattr(t2, 'identity') and \
           t2 not in env.itervalues():
            env[t1] = t2
            return True, env
        elif t1 in env and env[t1] == t2:
            return True, env
        else:
            return False, None

    try:
        if t1.head == t2.head:
            for st1, st2 in izip(t1.body, t2.body):
                success, env = alpha_eq(st1, st2, env)
                if not success:
                    return False, None
            return True, env
        return False, None
    except AttributeError:
        return False, None


def unify(t1, t2, env=None, type='simple'):
    """unify two terms to produce a substitution

    t1, t2: Terms
    env: the substitution
    type: 'simple' is for full unification
          'match' is for rewriting
          'alpha' is for alpha equivalence
    """
    try:  # treat t1 *and* t2 as applications
        if t1.head == t2.head:
            for (st1, st2) in izip(t1.body, t2.body):
                success, env = unify(st1, st2, env, type)
                if not success:
                    return False, None
            return True, env
        return False, None
    except AttributeError:
        pass

    try:  # treat t1 as variable
        return unify_var(t1, t2, env, type)
    except UnifyError:
        pass

    try:  # treat t2 as variable
        if type is 'simple':
            return unify_var(t2, t1, env, type)
    except UnifyError:
        pass
    return False, None


def unify_var(t1, t2, env, type='simple'):
    if hasattr(t1, 'identity'):
        if env is None:
            env = {}

        if t1 == t2:
            return True, env
        if t1 in env:
            return unify(env[t1], t2, env, type)
        if t2 in env:
            return unify(t1, env[t2], env, type)
        if type is not 'alpha' or hasattr(t2, 'identity'):
            env[t1] = t2
            return True, env
    else:
        raise UnifyError('unify-var: first arg must be a variable')


def differences(t1, t2):
    if t1 == t2:
        return []
    try:
        return [(t1, t2)] + list(chain(*[differences(st1, st2)
                                         for st1, st2 in izip(t1.body,
                                                              t2.body)]))
    except AttributeError:
        return [(t1, t2)]


def sample_rule(atom, operators, variables):
    atoms = set()
    side = 'lhs' if hasattr(atom, 'identity') else choice(['lhs', 'rhs'])
    if atom is None:
        side = 'neither'
    if atom is not None and atom not in operators | variables:
        raise ValueError('sample_rule: atom must be in signature')
    while atom not in atoms:
        lhs_signature = operators | variables
        if side == 'lhs':
            lhs = sample_term_c(lhs_signature, {atom})
        else:
            lhs = sample_term(lhs_signature)

        rhs_signature = operators | lhs.variables()
        if side == 'rhs':
            rhs = sample_term_c(rhs_signature, {atom})
        else:
            rhs = sample_term(rhs_signature)

        try:
            rule = RR(lhs, rhs)
            atoms = rule.operators() | rule.variables() | {None}
        except TRSError:
            atoms = set()

    return rule


def sample_rules(n, atom, operators, variables):
    return [sample_rule(atom, operators, variables) for _ in xrange(n)]


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
           for _ in range(20)]
    ps3 = [log_p_c(t, signature, {Op('S', 0), Op('K', 0)}) for t in ts3]
    for t, p in zip(ts3, ps3):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

    print 'terms | term, constraints'
    ts4 = [sample_term_tc(signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for _ in range(20)]
    ps4 = [log_p_tc(t, signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for t in ts4]
    for t, p in zip(ts4, ps4):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

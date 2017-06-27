from TeRF.Trees import possible_roots, head, leaves
from TeRF.TRS import App, Var, Op, RR
from numpy import exp
from numpy.random import choice, binomial
from itertools import repeat, izip
from TeRF.Miscellaneous import log0, log1of, gift, list_possible_gifts
from scipy.misc import logsumexp
from scipy.stats import geom
from copy import copy


class GenerationError(Exception):
    pass


def sample_head(signature, invent=True):
    head = choice(list(signature) + (['new var'] if invent else []))
    if head == 'new var':
        head = Var()
    return head


def log_p_head(head, signature, invent=True):
    if head in signature or (invent and hasattr(head, 'identity')):
        return -log0(len(signature) + (1 if invent else 0))
    return log0(0)


def sample_term(signature, invent=True):
    """
    sample a TRS term given a TRS signature

    Args:
      signature: an iterable containing TRS Operators and Variables
      invent: a boolean marking whether to invent variables
    Returns:
      a TRS term sampled from the grammar defined by signature
    """
    if leaves(signature) == [] and not invent:
        raise GenerationError('sample_term: no terminals!')
    sig = copy(signature)
    head = sample_head(sig, invent)
    sig |= {head}
    try:
        body = []
        for _ in repeat(None, head.arity):
            t = sample_term(sig, invent)
            body.append(t)
            sig |= t.variables
        return App(head, body)
    except AttributeError:
        return head


def log_p(term, signature, invent=True):
    """
    compute the probability of sampling a term given a signature

    Args:
      term: a TRS term
      signature: an iterable containing TRS Operators and Variables
      invent: a boolean marking whether to invent variables
    Returns:
      a float representing log(p(term | signature))
    """
    sig = copy(signature)
    p = log_p_head(head(term), sig, invent)
    sig |= ({head(term)} if invent else set())
    try:
        for t in term.body:
            p += log_p(t, sig, invent)
            sig |= (t.variables if invent else set())
    except AttributeError:
        pass
    return p


def sample_term_t(signature, term, p_r, invent=True):
    """
    generate a term conditioned on an existing term

    Args:
      signature: an iterable of TRS Operators and Variables
      term: a TRS term
      p_r: a float giving the node-wise probability of regeneration
    Returns:
      a TRS term
    """
    sig = copy(signature)
    if binomial(1, p_r):
        return sample_term(sig, invent)
    try:
        body = []
        for t in term.body:
            new_t = sample_term_t(sig, t, p_r, invent)
            body.append(new_t)
            sig |= new_t.variables
        return App(term.head, body)
    except AttributeError:
        return copy(term)


def log_p_t(new, signature, old, p_r, invent=True):
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
    if head(new) == head(old):
        p_make_head = log0(p_r) + log_p(new, signature, invent)
        p_keep_head = log0(1-p_r)
        try:
            for tn, to in izip(new.body, old.body):
                p_keep_head += log_p_t(tn, signature, to, p_r, invent)
                signature |= (tn.variables if invent else set())
        except AttributeError:
            pass
        return logsumexp([p_keep_head, p_make_head])
    return log0(p_r) + log_p(new, signature, invent)


def sample_term_c(signature, constraints, invent=True):
    """
    generate a term conditioned on a set of required symbols

    Args:
      signature: an iterable of TRS Operators and Variables
      constraints: an iterable subset of signature that must appear in term
      invent: a boolean marking whether to invent variables
    Returns:
      a TRS term
    Raises:
      GenerationError: raised when the signature or constraints are invalid
    """
    if leaves(signature) == [] and not invent:
        raise GenerationError('sample_term: no terminals!')
    sig = copy(signature)
    if not set(sig) >= set(constraints):
        raise GenerationError('sample_term_c: constraints not in signature')

    head = sample_head(possible_roots(sig, constraints),
                       invent and len(constraints) == 0)
    sig |= {head}

    try:
        constraint_assignments = gift(set(constraints)-{head}, head.arity)
        body = []
        for cs in constraint_assignments:
            t = sample_term_c(sig, cs)
            sig |= t.variables
            body.append(t)
        return App(head, body)
    except AttributeError:
        return head


def log_p_c(term, signature, constraints, invent=True):
    """
    compute the probability of sampling a term given a signature and term

    Args:
      term: a TRS term
      signature: an iterable of TRS Operators and Variables
      constraints: an iterable subset of signature that must appear in term
    Returns:
      a float representing log(p(term | signature, constraints))
    """
    if not set(signature) >= set(constraints):
        return log0(0)

    p = log_p_head(head(term), possible_roots(signature, constraints), invent)
    signature |= ({head(term)} if invent else set())

    try:
        who_has_what = [[(c if c in (t.variables | t.operators) else None)
                         for c in set(constraints)-{head(term)}]
                        for t in term.body]
        gifts = list_possible_gifts(who_has_what)
        ps_gifts = list(repeat(log1of(gifts), len(gifts)))
        for i, g in enumerate(gifts):
            new_sig = copy(signature)
            for t, cs in izip(term.body, g):
                ps_gifts[i] += log_p_c(t, new_sig, cs)
                new_sig |= (t.variables if invent else set())
        p += logsumexp(ps_gifts)
    except AttributeError:
        pass
    return p


def sample_term_tc(signature, term, p_r, constraints, invent=True):
    """
    generate a term conditioned on a term and a set of required symbols

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
        raise GenerationError('sample_term_tc: constraints not in signature')
    h = head(term)
    if binomial(1, p_r) or \
       (hasattr(h, 'identity') and not set(constraints) <= {h}) or \
       (hasattr(h, 'arity') and len(constraints) == 1 and h.arity < 1) or \
       (hasattr(h, 'arity') and len(constraints) > 1 and h.arity < 2):
        return sample_term_c(signature, constraints, invent)
    try:
        assignments = gift(set(constraints)-{h}, h.arity)
        body = []
        for t, cs in izip(term.body, assignments):
            new_t = sample_term_tc(signature, t, p_r, cs, invent)
            body.append(new_t)
            signature |= new_t.variables
        return App(term.head, body)
    except AttributeError:
        return copy(term)


def log_p_tc(new, signature, old, p_r, constraints, invent=True):
    """
    compute the probability of sampling a term given a term and constraints

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

    nh, oh = head(new), head(old)

    if (hasattr(oh, 'identity') and not set(constraints) <= {oh}) or \
       (hasattr(oh, 'arity') and len(constraints) == 1 and oh.arity < 1) or \
       (hasattr(oh, 'arity') and len(constraints) > 1 and oh.arity < 2):
        return log_p_c(new, signature, constraints, invent)

    p_make_head = log0(p_r) + log_p_c(new, signature, constraints, invent)
    if oh == nh:
        who_has_what = [[c if c in (t.variables | t.operators) else None
                         for c in set(constraints)-{oh}]
                        for t in new.body]
        gifts = list_possible_gifts(who_has_what)
        ps_gifts = list(repeat(log1of(gifts), len(gifts)))
        for i, g in enumerate(gifts):
            new_sig = copy(signature)
            for n, o, cs in izip(new.body, old.body, g):
                ps_gifts[i] += log_p_tc(n, new_sig, o, p_r, cs)
                new_sig |= (t.variables if invent else set())
        p_keep_head = log0(1-p_r) + logsumexp(ps_gifts)
        return logsumexp([p_make_head, p_keep_head])
    return p_make_head


def sample_rule(operators, variables, constraints=None,
                p_rhs=0.5, invent=True):
    if constraints is None or len(constraints) == 0:
        lhs = sample_term(operators | variables, invent)
        rhs = [sample_term(operators | lhs.variables, invent=False)
               for _ in repeat(None, geom.rvs(p_rhs))]
        return RR(lhs, rhs)

    if all(c in operators | variables for c in constraints):
        op_constraints = {c for c in constraints if hasattr(c, 'arity')}
        var_constraints = constraints - op_constraints

        lhs_constraints = var_constraints + {c for c in op_constraints
                                             if choice([True, False])}
        rhs_constraints = constraints - lhs_constraints

        lhs = sample_term_c(operators | variables, lhs_constraints, invent)
        rhs = [sample_term_c(operators | lhs.variables,
                             rhs_constraints, invent=False)
               for _ in repeat(None, geom.rvs(p_rhs))]
        return RR(lhs, rhs)
    raise GenerationError('sample_rule: constraints must be in signature')


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

    print '\nterms | terms'
    ts2 = [sample_term_t(signature, ts[0], 0.5) for _ in range(20)]
    ps2 = [log_p_t(t2, signature, ts[0], 0.5) for t2 in ts2]
    for t, p in zip(ts2, ps2):
        print '{} -> {}, {:f}, {:f}'.format(ts[0], t.pretty_print(), p, exp(p))

    print '\nterms | constraints'
    ts3 = [sample_term_c(signature, {Op('S', 0), Op('K', 0)})
           for _ in range(20)]
    ps3 = [log_p_c(t, signature, {Op('S', 0), Op('K', 0)}) for t in ts3]
    for t, p in zip(ts3, ps3):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

    print '\nterms | term, constraints'
    ts4 = [sample_term_tc(signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for _ in range(20)]
    ps4 = [log_p_tc(t, signature, ts[0], 0.2, {Op('S', 0), Op('K', 0)})
           for t in ts4]
    for t, p in zip(ts4, ps4):
        print '{}, {:f}, {:f}'.format(t.pretty_print(), p, exp(p))

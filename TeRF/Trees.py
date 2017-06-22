from itertools import chain, izip
from zss import distance


def head(term):
    try:
        return term.head
    except AttributeError:
        return term
    

def leaves(signature):
    return [atom for atom in signature
            if not hasattr(atom, 'arity') or atom.arity == 0]


def possible_roots(signature, must_haves):
    if len(must_haves) == 0:
        return list(signature)
    if len(must_haves) == 1:
        return [s for s in signature
                if s in must_haves or (hasattr(s, 'arity') and s.arity > 0)]
    return [s for s in signature if hasattr(s, 'arity') and s.arity > 1]


def edit_distance(t1, t2):
    def get_cs(t):
        return t.body if hasattr(t, 'body') else []

    def insert_c(t):
        return 1

    def remove_c(t):
        return 1

    def update_c(t1, t2):
        return 0 if t1 == t2 else 1

    return distance(t1, t2, get_cs, insert_c, remove_c, update_c)


def differences(t1, t2):
    """all mismatching pairs of corresponding subtrees in t1 & t2"""
    # TODO: What about mismatching heads and branches?
    if t1 == t2:
        return []
    try:
        return [(t1, t2)] + list(chain(*[differences(st1, st2)
                                         for st1, st2 in izip(t1.body,
                                                              t2.body)]))
    except AttributeError:
        return [(t1, t2)]

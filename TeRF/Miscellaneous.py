from itertools import repeat, product, izip
import numpy as np
from numpy.random import choice
from random import sample


def gift(xs, N):
    """
    give each x in xs to one of N recipients

    Args:
      xs: a finite iterable of gifts
      ys: a finite iterable of recipients
    Returns:
      a list of len(ys) lists of the xs given to each y
    """
    gifts = [[] for _ in repeat(None, N)]
    for x in xs:
        gifts[choice(N)] += [x]
    return gifts


def list_possible_gifts(who_owns_what):
    """
    list all possible ways to give objects to owners
    based on who currently owns each kind of object

    Args:
      xs: a finite iterable of gifts
      ys: a finite iterable of owners
    Returns:
      a list of possible giftings in the format of gift
    Raises: ValueError if not all objects have owners
    """
    what_is_whos = izip(*who_owns_what)
    if not all([any(owners) for owners in what_is_whos]):
        raise ValueError('list_possible_gifts: each object needs an owner')
    else:
        owner_idxs = [[i for i, x in enumerate(owners) if x is not None]
                      for owners in what_is_whos]
        proto_giftings = list(product(*owner_idxs))
        giftings = []
        for pg in proto_giftings:
            gifting = [[] for _ in who_owns_what]
            for item, owner in enumerate(pg):
                gifting[owner] += [who_owns_what[owner][item]]
            giftings += [gifting]
        return giftings


def find_insertion(xs1, xs2):
    """
    Find the item inserted into xs2 to create xs1

    Args:
      xs1: a list
      xs2: a list
    Returns:
      the item inserted into xs2 to create xs1
    """
    if len(xs1) - len(xs2) != 1:
        return None
    candidate = None
    c = 0
    for i in xrange(len(xs1)):
        if i == len(xs2) and candidate is None:
            return xs1[i]
        elif xs1[i] != xs2[i-c] and candidate is None:
            candidate = xs1[i]
            c = 1
        elif xs1[i] != xs2[i-c]:
            return None
    return candidate


def find_difference(xs1, xs2):
    if len(xs1) != len(xs2):
        return None, None
    candidates = [(x1, x2) for (x1, x2) in izip(xs1, xs2) if x1 != x2]
    if len(candidates) == 1:
        return candidates[0]
    return None, None


def logNof(xs, empty=0, n=1):
    return (log(n) - log(len(xs))) if xs != [] else log(empty)


def log(x):
    return -np.inf if x == 0.0 else np.log(x)


def log1mexp(x):
    return np.log1p(-np.exp(x)) if (x < log(.5)) else log(-np.expm1(x))


def unique_shuffle(xs):
    if len(set(xs)) <= 1:
        return None
    while True:
        result = sample(xs, len(xs))
        if xs != result:
            return result

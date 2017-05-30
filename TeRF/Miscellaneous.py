from numpy.random import choice
from itertools import repeat, product, izip


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
    if (len(xs1) - len(xs2)) != 1:
        return None
    candidates = [r for r in xs1 if r not in xs2]
    if len(candidates) == 1:
        return candidates[0]
    return None


def find_difference(xs1, xs2):
    if len(xs1) != len(xs2):
        return None, None
    candidates = [(x1, x2) for (x1, x2) in izip(xs1, xs2) if x1 != x2]
    if len(candidates) == 1:
        return candidates[0]
    return None, None

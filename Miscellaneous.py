from numpy.random import choice
import numpy as np
from itertools import product, permutations


def branch_assignment(xs, ys, exact=False, p=0.01):
    """
    give each x in xs to at least one y in ys
    
    Args:
      xs: a finite iterable of gifts
      ys: a finite iterable of recipients
      exact: boolean, whether to assign xs exactly once
      p: a float, the rate at which objects are given additional times
    Returns:
      a list of len(ys) lists of the xs given to each y
    """
    xs = list(xs)
    ys = list(ys)

    ps = np.array([p**x for x in range(len(ys))])
    ps /= sum(ps)

    gifts = [[] for y in ys]
    for x in xs:
        n = 1 if exact else choice(range(len(ys)), p=ps)+1
        chosen = choice(len(ys), n, replace=False)
        for y in range(len(ys)):
            if y in chosen:
                gifts[y] += [x]
    return gifts


def all_branch_assignments(xs, ys, p=0.01):

    ns = [range(1, len(ys)+1) for x in xs]
    assignments = []
    ps = []

    normed_ps = np.array([p**x for x in range(len(ys))])
    normed_ps /= sum(normed_ps)
    
    for counts in product(*ns):
        xyz = []
        for c in counts:
            places = [1]*c + [0]*(len(ys)-c)
            xyz.append(unique_permutations(places))
        proto_assignments = list(product(*xyz))
        for proto_assignment in proto_assignments:
            the_p = -np.log(len(proto_assignments))
            assignment = [[] for y in range(len(ys))]
            for x, x_asn in zip(xs, proto_assignment):
                the_p += np.log(normed_ps[sum(x_asn)-1])
                for i, place in enumerate(x_asn):
                    if place:
                        assignment[i] += [x]
            assignments.append(assignment)
            ps.append(the_p)
    return assignments, ps


def unique_permutations(xs):
    ps = []
    for p in permutations(xs):
        if p not in ps:
            ps.append(p)
    return ps

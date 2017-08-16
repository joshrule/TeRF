import copy
import itertools as iter
import numpy as np
import os
import scipy.stats as ss
import TeRF.Types.Operator as O
import TeRF.Types.Rule as R
import TeRF.Types.Signature as S
import TeRF.Types.TRS as TRS
import time


def write_sampled_trss(out_dir, p_operator, p_arity, p_rule, n_trss=1,
                       max_nodes=np.inf, signature=None):
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    written = []
    while len(written) < n_trss:
        str_n = ('{:0' + str(int(np.ceil(np.log10(n_trss)+1))) + 'd}').format(
            len(written)+1)
        out_file = os.path.join(out_dir, str_n + '.terf')
        if not os.path.exists(out_file):
            try:
                trs = sample_trs(p_operator, p_arity, p_rule, signature)
            except ValueError:
                continue
            if sum(len(r.lhs) + len(r.rhs0) for r in trs.rules()) <= max_nodes:
                written += [out_file]
                trs.save(out_file)
        else:
            written += [out_file]
    return written


def sample_trs(p_operator, p_arity, p_rule, signature=None):
    trs = TRS.TRS()

    if signature is None:
        for _ in xrange(ss.geom.rvs(p=p_operator)):
            trs.signature.add(O.Op(arity=ss.geom.rvs(p=p_arity)-1))
    else:
        trs.signature = signature
        trs.signature.parent = trs

    n_rules = ss.geom.rvs(p=p_rule)
    tries = 0
    while trs.num_rules() < n_rules and tries < 10*n_rules:
        sampled = trs.signature.sample_rule(p_rhs=1.0, invent=True)
        trs.add(sampled)
        tries += 1
    if trs.num_rules() < n_rules:
        raise ValueError('make_tests.sample_trs: could not sample trs')

    return trs


def write_enumerated_trss(out_dir, signature, max_nodes):
    for N in xrange(max_nodes+1):
        n_dir = os.path.join(out_dir, str(N))
        if not os.path.isdir(n_dir):
            os.mkdir(n_dir)
        for i, trs in enumerate(enumerate_trss_with_N_nodes(signature, N)):
            out_file = os.path.join(n_dir, str(N) + '_' + str(i) + '.terf')
            if not os.path.exists(out_file):
                trs.save(out_file)


def enumerate_trss(signature, max_nodes):
    return iter.chain(*(
        enumerate_trss_with_N_nodes(signature, N)
        for N in xrange(1, max_nodes+1)))


def enumerate_trss_with_N_nodes(signature, N):
    return iter.chain(*[
        enumerate_trss_with_assignment(signature, assignment)
        for assignment in assign_nodes_to_rules(N)])


def assign_nodes_to_rules(nodes):
    if nodes < 2:
        return []
    assignments = []
    for l in xrange(1, nodes):
        for r in xrange(1, nodes-l+1):
            if l+r == nodes:
                assignments += [[(l, r)]]
            else:
                assignments += [[(l, r)] + part
                                for part in assign_nodes_to_rules(nodes-(l+r))]
    return assignments


def enumerate_trss_with_assignment(signature, assignment):
    rulesets = enumerate_rulesets_with_assignment(signature, assignment)
    trss = []
    for ruleset in rulesets:
        trs = TRS.TRS()
        trs.signature = signature
        for i, rule in enumerate(ruleset):
            trs[i] = copy.deepcopy(rule)
        trss.append(trs)
    return trss


def enumerate_rulesets_with_assignment(signature, assignment, partial=None):
    if assignment:
        partial = partial if partial is not None else []
        # create the list of rules, filtering out identity rules
        l, r = assignment[0]
        rules = [rule for rule in enumerate_rules_at(signature, l, r)]

        # then, filter the identities, duplicates, and parities
        rules = filter_rules(rules, partial, enumerated=True)

        # from what remains, select each rule and recurse
        enums = [enumerate_rulesets_with_assignment(signature,
                                                    assignment[1:],
                                                    partial + [rule])
                 for rule in rules]

        return list(iter.chain(*enums))
    return [partial]


def filter_rules(rules, partial, enumerated=False):
    no_ids = [rule for rule in rules if rule.lhs != rule.rhs0]
    no_ids_dups = [rule for rule in no_ids if rule not in partial]
    env = {op: op for rule in partial for op in rule.operators}
    no_ids_dups_partials = filter_parities(no_ids_dups, env, enumerated)
    return no_ids_dups_partials


def filter_parities(rules, env=None, enumerated=False):
    env = {} if env is None else env
    solution = []
    if enumerated:
        lhss = [r.lhs for r in rules]
        unique_lhss = []
        while lhss:
            unique_lhss.append(lhss[0])
            lhss = [lhs for lhs in lhss[1:]
                    if lhss[0].parity(lhs, env.copy()) is None]
        rules = [rule for rule in rules if rule.lhs in unique_lhss]
    while rules:
        solution.append(rules[0])
        rules = [rule for rule in rules[1:]
                 if rules[0].parity(rule, env.copy()) is None]
    return solution


def make_a_rule(lhs, rhs):
    try:
        return R.Rule(lhs, rhs)
    except:
        pass


def enumerate_rules_at(signature, lhs_n, rhs_n):
    rules = []
    for lhs in signature.enumerate_at(lhs_n, True):
        rhs_sig = signature.copy()
        for a in lhs.atoms:
            rhs_sig.add(a)
        for rhs in rhs_sig.enumerate_at(rhs_n, False):
            rules.append(make_a_rule(lhs, rhs))
    return [r for r in rules if r is not None]


if __name__ == "__main__":
    a = O.Op('A', 0)
    b = O.Op('B', 0)
    c = O.Op('C', 0)
    app = O.Op('.', 2)
    sig = S.Signature({a, b, c, app})

    res1 = enumerate_rules_at(sig, 1, 1)
    print 'enumerated 1 = 1 rules'
    for rule in res1:
        print rule
    print

    res2 = filter_rules(res1, [])
    print 'filtered 1 = 1 rules'
    for rule in res2:
        print rule
    print

    assignment = [(1, 1), (1, 1)]
    res3 = enumerate_rulesets_with_assignment(sig, assignment)
    print '1=1; 1=1; rulesets'
    for ruleset in res3:
        for rule in ruleset:
            print rule
        print

    res4 = enumerate_trss_with_assignment(sig, assignment)
    print '1=1; 1=1; TRSs'
    for trs in res4:
        print trs
        print

    N = 4
    res5 = assign_nodes_to_rules(N)
    print '4 node assignments'
    for assignment in res5:
        print assignment
    print

    res6 = list(enumerate_trss_with_N_nodes(sig, N))
    print '4 node TRSs:'
    for trs in res6:
        print trs
        print

    print 'Total number of 4 node TRSs:'
    print len(list(enumerate_trss_with_N_nodes(sig, 4))), '\n'
    print 'Total number of 6 node TRSs:'
    print len(list(enumerate_trss_with_N_nodes(sig, 6))), '\n'
    
#     N = 10
#     start = time.time()
#     res7 = list(enumerate_trss(sig, N))
#     end = time.time()
#     print 'Total number of TRSs with', N, 'nodes or less:', len(res7)
#     print 'elapsed time to enumerate them:', end-start

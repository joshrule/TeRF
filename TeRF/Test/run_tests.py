import copy
import joblib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import dill
import sys
import TeRF.Language.parser as parser
import TeRF.Learning.TRSHypothesis as TRSH
import TeRF.Miscellaneous as misc
import TeRF.Test.make_tests as mt
import TeRF.Test.test_sampler as ts
import TeRF.Types.Application as A
import TeRF.Types.Rule as R
import TeRF.Types.TRS as TRS
import time


def load_signature(sig_file):
    if sig_file is '':
        return None
    trs, _ = parser.load_source(sig_file)
    return trs.signature


def sample_problems(rc):
    sig = load_signature(rc.signature_file)
    n0s = int(np.ceil(np.log10(rc.n_problems)))
    trs_files = [misc.mkdir(rc.prob_dir + '/' + str(i).zfill(n0s) + '.terf')
                 for i in xrange(rc.n_problems)]
    for trs_file in trs_files:
        while not os.path.exists(trs_file):
            try:
                trs = mt.sample_trs(rc.p_operator, rc.p_arity, rc.p_rule, sig)
                if sum(r.complexity for r in trs.rules()) <= rc.max_nodes:
                    trs.save(trs_file)
            except ValueError:
                continue
    return trs_files


def run_tests(rcs, res_file):
    start = time.strftime("%Y %b %d %H:%M:%S %Z")
    records = joblib.Parallel(n_jobs=-1)(
        joblib.delayed(run_test)(rc) for rc in rcs)
    stop = time.strftime("%Y %b %d %H:%M:%S %Z")
    results = pandas.DataFrame.from_records(records)
    results.to_csv(res_file)
    return results, start, stop


def report_results(out_f, results, start_time, stop_time):
    with open(out_f, 'w') as f:
        f.write('This test of TeRF\n\n')
        f.write('\n* started at {},\n\n'.format(start_time))
        f.write('* ended at {},\n\n'.format(stop_time))
        f.write('* had the following individual results:\n')

        s_succs = []
        f_succs = []
        e_succs = []
        for file in set(results['e_trs_f']):
            res_slice = results[results.e_trs_f == file]
            n_tries = len(res_slice.index)
            s_succ = len(res_slice[res_slice.diff_score >= 0.0].index)
            f_succ = len(res_slice[res_slice.any_correct].index)
            e_succ = len(res_slice[res_slice.h_map_correct].index)
            s_succs.append(s_succ)
            f_succs.append(f_succ)
            e_succs.append(e_succ)
            s_perc = 100.0 * float(s_succ) / float(n_tries)
            f_perc = 100.0 * float(f_succ) / float(n_tries)
            e_perc = 100.0 * float(e_succ) / float(n_tries)
            f.write('  - {}:\n'.format(file))
            p_str = '      - {}: {:d}/{:d} = {:.2f}%...{}\n'
            f.write(p_str.format('p(MAP|d) > p(h*|d)', s_succ, n_tries,
                                 s_perc, 'PASS' if s_succ else 'FAIL'))
            f.write(p_str.format('finds h*', f_succ, n_tries,
                                 f_perc, 'PASS' if f_succ else 'FAIL'))
            f.write(p_str.format('MAP is h*', e_succ, n_tries,
                                 e_perc, 'PASS' if e_succ else 'FAIL'))
            trs, _ = parser.load_source(file)
            trs.prettify()
            f.write('\n    ' + str(trs).replace('\n', '\n    ') + '\n\n')
        f.write('\n* and can be summarized as follows:\n')
        tt = len(s_succs)
        s_pd = sum(1 for s in s_succs if s)
        s_pt = 100.0 * float(s_pd) / float(tt)
        f_pd = sum(1 for s in f_succs if s)
        f_pt = 100.0 * float(f_pd) / float(tt)
        e_pd = sum(1 for s in e_succs if s)
        e_pt = 100.0 * float(e_pd) / float(tt)
        p_str = '  - {}: {:d}/{:d} = {:.2f}% PASSED\n'
        f.write(p_str.format('p(MAP|d) > p(h*|d)', s_pd, tt, s_pt))
        f.write(p_str.format('finds h*', f_pd, tt, f_pt))
        f.write(p_str.format('MAP is h*', e_pd, tt, e_pt))


def plot_results(out_dir, results):
    # hack! figure out how to learn these programatically
    for feature in ['n_rules', 'n_nodes', 'n_lhss', 'mean_rule_len',
                    'max_rule_len', 'n_vars', '%_vars', 'n_nondet_rules',
                    'n_nondets', '%_nondets']:
        plot_file = misc.mkdir(os.path.join(out_dir, feature + '.svg'))
        plot_feature(plot_file, feature, results[feature], results.diff_score)


def plot_feature(out_file, feature, feats, scores):
    plt.gcf().clf()
    plt.plot(feats, scores, 'ko')
    plt.xlabel(feature)
    plt.ylabel(r'$p(h_{MAP} | data) - p(h^\ast | data)$')
    plt.title('Goodness of fit for ' + feature)
    plt.grid(which='major', axis='y')
    plt.tight_layout()
    plt.savefig(out_file)


def run_test(rc):
    print rc.test, '-', rc.chain
    dill_f = os.path.join(rc.result_dir, 'results.dill')
    if not os.path.exists(dill_f):
        data, h0, h_star = prepare_for_test(rc)
        del rc.reqs  # for pickling, etc.
        hs = test(h0, data, rc.sampler_args, rc.test_log)
        results = summarize_test(rc, hs, h_star, data)
        with open(dill_f, 'wb') as d:
            dill.dump(results, d)
            dill.dump(hs, d)
    with open(dill_f, 'rb') as d:
        return dill.load(d)


def log_problem(rc, data=None, h0=None, h_star=None, h_gen=None,
                human_data=None):
    with open(rc.problem_log, 'w') as f:
        f.write('Problem Configuration\n')
        for k, v in rc.__dict__.iteritems():
            f.write('{}: {}\n'.format(k, v))
        if data is not None:
            f.write('\nObserved Data:\n')
            for datum in data:
                f.write(str(datum) + '\n')
        if h_gen is not None:
            f.write('\nGeneration (START -> LHS) Theory:\n')
            f.write(str(h_gen) + '\n')
        if h_star is not None:
            f.write('\nEvaluation (LHS -> RHS) Theory (H*):\n')
            f.write(str(h_star) + '\n')
        if h0 is not None:
            f.write('\nInitial Theory (H0):\n' + str(h0) + '\n')
    if human_data is not None:
        human_log = rc.problem_log + '.human_data'
        with open(human_log, 'w') as f:
            f.write('\nObserved Data:\n')
            for datum in human_data:
                f.write(str(datum) + '\n')


def prepare_for_test(rc):
    g_trs, _ = parser.load_source(rc.g_trs_f)
    e_trs, _ = parser.load_source(rc.e_trs_f,
                                  signature=g_trs.signature.copy())
    start = A.App(g_trs.signature.find(rc.start), [])
    ops_to_change = [op for op in e_trs.signature if op.name in rc.symbols]

    data_dir = misc.mkdir(os.path.join(rc.result_dir, 'data/'))
    data, human_data = make_data(e_trs, g_trs, data_dir, rc.reqs, start,
                                 ops_to_change)
    h0 = make_hypothesis(rc.p_partial, rc.p_operator, rc.p_arity, rc.p_rule,
                         rc.p_r, data=data)
    h_star = make_hypothesis(rc.p_partial, rc.p_operator, rc.p_arity,
                             rc.p_rule, rc.p_r, trs=e_trs)

    if rc.problem_log is not None:
        log_problem(rc, data, h0, h_star, g_trs, human_data)

    return data, h0, h_star


def test(h0, data, sampler_args, log_file=None):
    if log_file is not None:
        saveout, saveerr = sys.stdout, sys.stderr
        o = open(os.path.join(log_file), 'w', 1)
        sys.stdout, sys.stderr = o, o

    start = time.time()
    hs = ts.test_sample(
        h0, data, N=10, trace=False, show_skip=0, show=(log_file is not None),
        **sampler_args)
    stop = time.time()

    if log_file is not None:
        print '# time spent sampling: {:.2f}s'.format(stop-start)
        print '#\n#\n# The best hypotheses discovered:'
        for h in hs.get_all(sorted=True):
            print '#\n#', h.prior, h.likelihood, h.posterior_score
            print '#', str(h).replace('\n', '\n# ')

        sys.stdout, sys.stderr = saveout, saveerr
        o.close()

    return hs


def summarize_test(rc, hs, h_star, data):
    results = h_star.value.features()
    results.update(rc.__dict__)
    results['map_score'] = hs.best().compute_posterior(data)
    results['true_score'] = h_star.compute_posterior(data)
    results['diff_score'] = results['map_score'] - results['true_score']
    results['any_correct'] = any(h_star.value.unifies(h.value) for h in hs)
    results['h_map_correct'] = h_star.value.unifies(hs.best().value)
    return results


def make_hypothesis(p_partial, p_operator, p_arity, p_rule, p_r, data=None,
                    trs=None):
    if trs is not None:
        hyp = trs
    elif data is not None:
        hyp = TRS.TRS()
        for rule in data:
            for op in rule.operators:
                hyp.signature.add(op)
    else:
        raise ValueError('run_tests.make_hypothesis: no value!')

    return TRSH.TRSHypothesis(value=hyp,
                              data=data,
                              privileged_ops=hyp.signature.operators,
                              p_partial=p_partial,
                              p_operators=p_operator,
                              p_arity=p_arity,
                              p_rules=p_rule,
                              p_r=p_r,
                              likelihood_temperature=0.1)


def make_data(e_trs, g_trs, data_dir, reqs, start, ops_to_change):
    data = TRS.TRS()
    data.signature = e_trs.signature.copy(parent=data)

    # load & test the existing data
    data_fs = misc.find_files(misc.mkdir(data_dir))
    for datum_f in data_fs:
        with open(datum_f, 'rb') as dill_f:
            datum = dill.load(dill_f)
        meet_reqs = [r(datum) for r in reqs]
        if any(meet_reqs):
            data.add(datum)
        else:
            os.remove(datum_f)
        reqs = [r for p, r in zip(meet_reqs, reqs) if not p]

    # sample any data we still need
    while reqs != []:
        trace = start.rewrite(g_trs, max_steps=100, type='one',
                              trace=True, strategy='eager')
        terms = [s.term for s in trace.root.leaves(states=['normal'])]
        try:
            lhs = terms[0]
        except IndexError:
            continue
        rhs = lhs.rewrite(e_trs, max_steps=100, type='one')
        datum = R.Rule(lhs, rhs)
        meet_reqs = [r(datum) for r in reqs]
        if any(meet_reqs):
            data.add(datum)
            datum_f = os.path.join(data_dir, str(data.num_rules()) + '.pkl')
            with open(datum_f, 'wb') as dill_f:
                dill.dump(datum, dill_f)
            reqs = [r for p, r in zip(meet_reqs, reqs) if not p]

    human_data = copy.deepcopy(data)
    human_data.prettify(change=ops_to_change)

    return list(data.rules()), list(human_data.rules())

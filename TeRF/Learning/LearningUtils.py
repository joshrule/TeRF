import dill
import joblib
import matplotlib.pyplot as plt
import os
import pandas
import sys
import tempfile
import TeRF.Language.parser as parser
import TeRF.Learning.LOTHypothesis as LOTH
import TeRF.Learning.sample as ts
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A
import TeRF.Types.Rule as R
import TeRF.Types.Trace as T
import time


def run_tests(rcs, res_file, n_jobs=-1):
    start = time.strftime("%Y %b %d %H:%M:%S %Z")
    records = joblib.Parallel(n_jobs=n_jobs)(
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
    hs = ts.sample(
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


def load_datum(datum_filename):
    with open(datum_filename, 'rb') as dill_f:
        return dill.load(dill_f)


def load_data(data_dir):
    data_fs = misc.find_files(misc.mkdir(data_dir))
    return [load_datum(data_f) for data_f in data_fs]


def save_data(data, data_dir):
    for datum in data:
        save_datum(datum, data_dir)


def save_datum(datum, data_dir):
    tempfile.tempdir = data_dir
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        dill.dump(datum, temp)


def make_hypothesis(p_partial, p_rule, lot, data):
    return LOTH.LOTHypothesis(value=lot,
                              data=data,
                              p_partial=p_partial,
                              p_rule=p_rule,
                              prior_temperature=1.,
                              likelihood_temperature=1.)


def make_data(e_g, g_g, start, data_dir, reqs):
    data = []
    candidates = load_data(data_dir)
    while reqs != []:
        datum = candidates.pop() if candidates else sample_datum(e_g, g_g, start)
        print 'datum', len(data), datum
        meet_reqs = [r(datum) for r in reqs]
        if any(meet_reqs):
            data.append(datum)
            reqs = [r for p, r in zip(meet_reqs, reqs) if not p]
    return data


def sample_datum(e_g, g_g, start):
    rule = None
    while rule is None:
        try:
            lhs = T.Trace(g_g, start, max_steps=100, type='one',
                          strategy='eager').rewrite(states=['normal'],
                                                    trace=False)
        except IndexError:
            pass

        rhs = T.Trace(e_g, lhs, max_steps=100, type='one',
                      strategy='eager').rewrite(states=['normal'], trace=False)

        try:
            rule = R.Rule(lhs, rhs)
        except ValueError:
            pass
    return rule

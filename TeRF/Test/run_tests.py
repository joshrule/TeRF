import collections
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
import yaml


rc = collections.namedtuple('rc', [
    'out_dir',
    'gen_theory',
    'res_dir',
    'res_file',
    'plot_dir',
    'prob_dir',
    'signature_file',
    'start_string',
    'p_operator',
    'p_arity',
    'p_rule',
    'p_r',
    'p_observe',
    'p_similar',
    'max_nodes',
    'n_chains',
    'n_steps',
    'n_problems',
    'n_changed',
    'n_total'])


def main(rcfile):
    rc = load_config(rcfile)
    # test_files = sample_problems(rc)
    # need to adapt this to make rcs for each test file
    results, start, stop = run_tests(rc)
    report_results(rc, results, start, stop)
    plot_results(misc.mkdir(rc.plot_dir), results)


def load_config(rcfile):
    with open(rcfile, 'r') as the_file:
        return rc(**yaml.safe_load(the_file))


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

        successes = []
        for file in set(results['e_trs_f']):
            res_slice = results[results.e_trs_f == file]
            n_tries = len(res_slice.index)
            succ = len(res_slice[res_slice.diff_score >= 0.0].index)
            successes.append(succ)
            perc = 100.0 * float(succ) / float(n_tries)
            f.write('  - {}: {:d}/{:d} = {:.2f}%...{}\n'.format(
                file, succ, n_tries, perc, 'PASS' if succ else 'FAIL'))
            trs, _ = parser.load_source(file)
            f.write('    ' + str(trs).replace('\n', '\n    ') + '\n\n')
        pd = sum(1 for s in successes if s)
        tt = len(successes)
        fd = tt-pd
        pt = 100.0 * float(pd) / float(tt)
        f.write('\n* and can be summarized as follows:\n')
        f.write('  - PASSED: {0:d}/{1:d} = {2:.2f}%\n'.format(pd, tt, pt))
        f.write('  - FAILED: {0:d}/{1:d} = {2:.2f}%\n'.format(fd, tt, 100-pt))


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
    dill_f = os.path.join(rc.result_dir, 'results.pkl')
    if not os.path.exists(dill_f):
        data, h0, h_star = prepare_for_test(rc)
        del rc.reqs  # for pickling, etc.
        hs = test(h0, data, rc.n_steps, rc.test_log)
        results = summarize_test(rc, hs.best(), h_star, data)
        with open(dill_f, 'wb') as d:
            dill.dump(results, d)
            dill.dump(hs, d)
    with open(dill_f, 'rb') as d:
        return dill.load(d)


def log_problem(rc, data=None, h0=None, h_star=None, h_gen=None):
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


def prepare_for_test(rc):
    g_trs, _ = parser.load_source(rc.g_trs_f)
    e_trs, _ = parser.load_source(rc.e_trs_f,
                                  signature=g_trs.signature.copy())
    start = A.App(g_trs.signature.find(rc.start), [])

    data_dir = misc.mkdir(os.path.join(rc.result_dir, 'data/'))
    data = make_data(e_trs, g_trs, data_dir, rc.reqs, start)
    h0 = make_hypothesis(rc.p_observe, rc.p_similar, rc.p_operator,
                         rc.p_arity, rc.p_rule, rc.p_r, data=data)
    h_star = make_hypothesis(rc.p_observe, rc.p_similar, rc.p_operator,
                             rc.p_arity, rc.p_rule, rc.p_r, trs=e_trs)

    if rc.problem_log is not None:
        log_problem(rc, data, h0, h_star, g_trs)

    return data, h0, h_star


def test(h0, data, n_steps, log_file=None):
    if log_file is not None:
        saveout, saveerr = sys.stdout, sys.stderr
        o = open(os.path.join(log_file), 'w', 1)
        sys.stdout, sys.stderr = o, o

    start = time.time()
    hs = ts.test_sample(
        h0, data, N=10, trace=False, likelihood_temperature=0.1,
        steps=n_steps, show_skip=0, show=(log_file is not None))
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


def summarize_test(rc, h_map, h_star, data):
    results = h_star.value.features()
    results.update(rc.__dict__)
    results['map_score'] = h_map.compute_posterior(data)
    results['true_score'] = h_star.compute_posterior(data)
    results['diff_score'] = results['map_score'] - results['true_score']
    return results


def make_hypothesis(p_observe, p_similar, p_operator, p_arity,
                    p_rule, p_r, data=None, trs=None):
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
                              p_observe=p_observe,
                              p_similar=p_similar,
                              p_operators=p_operator,
                              p_arity=p_arity,
                              p_rules=p_rule,
                              p_r=p_r)


def make_data(e_trs, g_trs, data_dir, reqs, start, quiet=False):
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

    return list(data.rules())

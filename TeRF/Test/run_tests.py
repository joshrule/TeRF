import collections
import joblib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import pickle
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
    test_files = sample_problems(rc)
    results, start, stop = run_tests(test_files, rc)
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


def run_tests(test_files, rc):
    test_fs = [(t, misc.mkdir(os.path.join(rc.res_dir, misc.stem(t), str(c))))
               for t in test_files for c in xrange(rc.n_chains)]

    start = time.strftime("%Y %b %d %H:%M:%S %Z")
    records = joblib.Parallel(n_jobs=-1)(joblib.delayed(run_test)(
        in_f, out_f, rc) for in_f, out_f in test_fs)
    stop = time.strftime("%Y %b %d %H:%M:%S %Z")

    results = pandas.DataFrame.from_records(records)
    results.to_csv(rc.res_file)
    return results, start, stop


def report_results(rc, results, start_time, stop_time):
    with open(os.path.join(rc.out_dir, 'README'), 'w') as f:
        f.write('This test of TeRF\n\n')
        f.write('* used the following parameters:\n\n')
        for k, v in rc._asdict().iteritems():
            f.write('  - {}: {}\n'.format(k, v))
        f.write('\n* started at {},\n\n'.format(start_time))
        f.write('* ended at {},\n\n'.format(stop_time))
        f.write('* had the following individual results:\n')

        successes = []
        for file in set(results['file']):
            res_slice = results[results.file == file]
            n_tries = len(res_slice.index)
            succ = len(res_slice[res_slice.diff_score >= 0.0].index)
            successes.append(succ)
            fail = n_tries-succ
            perc = 100.0 * float(succ) / float(n_tries)
            f.write('  - {}: {:d}/{:d} = {:.2f}%...{}\n'.format(
                file, succ, fail, perc, 'PASS' if succ else 'FAIL'))
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
    features = results.columns.tolist()
    features.remove('map_score')
    features.remove('diff_score')
    features.remove('true_score')
    features.remove('file')
    for feature in features:
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


def run_test(in_file, out_stem, rc):
    pickle_file = out_stem + '.pkl'
    if not os.path.exists(pickle_file):
        saveout, saveerr = sys.stdout, sys.stderr
        with open(out_stem + '.log', 'w', 1) as o:
            sys.stdout, sys.stderr = o, o

            data, h0, h_star = prepare_for_test(rc, in_file)
            hs = test(h0, data, rc.n_steps)

            sys.stdout, sys.stderr = saveout, saveerr
        results = summarize_results(hs.best(), h_star, data, in_file)
        with open(pickle_file, 'wb') as pkl:
            pickle.dump(results, pkl)
            # pickle.dump(hs, pkl)
    with open(pickle_file, 'rb') as pkl:
        return pickle.load(pkl)


def prepare_for_test(rc, in_file):
    g_trs, _ = parser.load_source(rc.gen_theory)
    e_trs, _ = parser.load_source(in_file,
                                  signature=g_trs.signature.copy())
    start = A.App(g_trs.signature.find(rc.start_string), [])

    data = make_data(e_trs, g_trs, rc.n_changed, rc.n_total, start)
    h0 = make_hypothesis(rc.p_observe, rc.p_similar, rc.p_operator,
                         rc.p_arity, rc.p_rule, rc.p_r, data=data)
    h_star = make_hypothesis(rc.p_observe, rc.p_similar, rc.p_operator,
                             rc.p_arity, rc.p_rule, rc.p_r, trs=e_trs)

    print '# Generating Theory:\n# ' + str(g_trs).replace('\n', '\n# ') + '\n#'
    print '# Evaluating Theory (H*):\n# ' + str(e_trs).replace('\n', '\n# ')
    print '#\n# Observed Data:'
    for datum in data:
        print '# ', datum
    print '#'
    print '# H0:\n# ' + str(h0).replace('\n', '\n# ') + '\n#'

    return data, h0, h_star


def test(h0, data, n_steps):
    start = time.time()
    hs = ts.test_sample(h0, data, N=10, trace=False, show_skip=0,
                        steps=n_steps, likelihood_temperature=0.5)
    stop = time.time()

    print '# time spent sampling: {:.2f}s'.format(stop-start)
    print '#\n#\n# The best hypotheses discovered:'
    for h in hs.get_all(sorted=True):
        print '#\n#', h.prior, h.likelihood, h.posterior_score
        print '#', str(h).replace('\n', '\n# ')

    return hs


def summarize_results(h_map, h_star, data, in_file):
    results = h_star.value.features()
    results['file'] = in_file
    results['map_score'] = h_map.compute_posterior(data)
    results['true_score'] = h_star.compute_posterior(data)
    results['diff_score'] = results['true_score'] - results['map_score']
    return results


def make_data(e_trs, g_trs, nChanged, nTotal, start_sym):
    data = TRS.TRS()
    data.signature = e_trs.signature.copy(parent=data)

    print '# Generating data starting from:', start_sym
    start = time.time()
    trace = start_sym.rewrite(g_trs, max_steps=11, type='all', trace=True)
    stop = time.time()
    states = trace.root.leaves(states=['normal'])
    terms = [s.term for s in states]
    ps = misc.normalize([s.log_p*0.5 for s in states])  # *0.5 weakens decay
    print '# {:d} LHSs generated in {:.2f}s'.format(len(terms), stop-start)

    start = time.time()
    tries = 0
    while data.num_rules() < nTotal:
        tries += 1
        lhs = np.random.choice(terms, p=ps)
        rhs = lhs.rewrite(e_trs, max_steps=7, type='one')
        rule = R.Rule(lhs, rhs)
        if ((data.num_rules() < nChanged and lhs != rhs) or
            (data.num_rules() >= nChanged and lhs == rhs) or
            (tries >= len(terms)*0.1)) and \
           (rule not in e_trs):
            data.add(rule)
    stop = time.time()
    print '# {:d} rules selected in {:.2f}s and {:d} tries\n#'.format(
        nTotal, stop-start, tries)

    return list(data.rules())


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

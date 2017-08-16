import collections
import itertools as iter
import joblib
import LOTlib.Inference.Samplers.StandardSample as ss
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas
import pickle
import re
import scipy.misc as sm
import sys
import TeRF.Language.parser as parser
import TeRF.Learning.TRSHypothesis as TRSH
import TeRF.Test.make_tests as mt
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


def sample_main(rcfile):
    rc = load_config(rcfile)

    ensure_dir(rc.out_dir)

    if rc.signature_file is not '':
        t, _ = parser.load_source(rc.signature_file)
        signature = t.signature
    else:
        signature = None

    start_time = time.strftime("%Y %b %d %H:%M:%S %Z")
    trss = mt.write_sampled_trss(rc.prob_dir, rc.p_operator, rc.p_arity,
                                 rc.p_rule, n_trss=rc.n_problems,
                                 max_nodes=rc.max_nodes, signature=signature)
    results = run_tests(trss, rc.res_dir, rc)
    stop_time = time.strftime("%Y %b %d %H:%M:%S %Z")

    results.to_csv(rc.res_file)
    report_results(rc, results, start_time, stop_time)
    plot_results(ensure_dir(rc.plot_dir), results)


def load_config(rcfile):
    with open(rcfile, 'r') as the_file:
        return rc(**yaml.safe_load(the_file))


def ensure_dir(the_dir):
    if not os.path.exists(the_dir):
        os.mkdir(the_dir)
    return the_dir


def status(string):
    print '='*80
    print string
    print '='*80 + '\n'


def main(problem_dir, out_dir, n_problems, gen_theory, start,
         n_chains=3, n_steps=3200):
    status('It Begins')
    problems = choose_problems(problem_dir, n_problems)
    report_results(run_tests(problems, out_dir, gen_theory, start,
                             n_chains, n_steps))


def choose_problems(problem_dir, n_problems):
    problems, ps = list_problems(problem_dir)
    problems = np.random.choice(problems, replace=False, size=n_problems, p=ps)
    status('Selected Test Problems')
    for i, prob in enumerate(problems):
        print '{:d}: {}'.format(i, prob)
        trs, _ = parser.load_source(prob)
        digits = 1 + (np.floor(np.log10(i)) if i > 0 else 0)
        pad = ' '*int(digits+2)
        print pad + str(trs).replace('\n', '\n' + pad)
        print
    return problems


def list_problems(dir, mass=1.0):
    terf = re.compile('.+\.terf$')
    problems, ps = [], []
    files = os.listdir(dir)
    if not files:
        return problems, ps
    mass_per_file = mass/float(len(files))
    for file in files:
        if os.path.isdir(os.path.join(dir, file)):
            f_problems, f_ps = list_problems(os.path.join(dir, file),
                                             mass_per_file)
            problems += f_problems
            ps += f_ps
        elif re.match(terf, file):
            problems.append(os.path.join(dir, file))
            ps.append(mass_per_file)
    return problems, list(np.array(ps)/sum(ps))


def run_tests(problems, out_dir, rc):
    ensure_dir(out_dir)
    dirs = [ensure_dir(os.path.join(out_dir,
                                    os.path.splitext(os.path.basename(p))[0]))
            for p in problems]
    results = joblib.Parallel(n_jobs=-1)(
        joblib.delayed(test)(p, os.path.join(d, str(c) + '.log'), rc)
        for p, d in iter.izip(problems, dirs) for c in xrange(rc.n_chains))
    df_src = []
    for r in results:
        trs, _ = parser.load_source(r[0])
        features = trs.features()
        features['file'] = r[0]
        features['success'] = r[1]
        df_src.append(features)
    return pandas.DataFrame.from_records(df_src)


def plot_results(out_dir, results):
    features = results.columns.tolist()
    features.remove('success')
    features.remove('file')
    for feature in features:
        plot_file = os.path.join(os.path.join(out_dir, feature + '.svg'))
        plot_feature(plot_file, feature, results[feature], results['success'])


def plot_feature(out_file, feature, feats, successes):
    hist, bins = np.histogram(feats, bins='auto')
    bin_ls, bin_rs = bins[:-1], bins[1:]

    ns = []
    ps = []
    for l, r in iter.izip(bin_ls, bin_rs):
        if r == bins[-1]:
            xs = successes[(l <= feats) | (feats <= r)]
        else:
            xs = successes[(l <= feats) | (feats < r)]
        ns.append(len(xs))
        ps.append(float(sum(xs))/float(len(xs)))

    widths = bin_rs - bin_ls

    plt.gcf().clf()
    plt.bar(bin_ls, ps, width=widths, align='edge')

    centers = (bin_ls + bin_rs) / 2
    err = [np.sqrt(p*(1-p)/n) for p, n in iter.izip(ps, ns)]
    plt.errorbar(centers, ps, xerr=err, fmt="none")

    plt.xlabel(feature)
    plt.ylabel('p(Success)')
    plt.title('Conditional probability of success discretized by ' + feature)
    plt.grid(which='major', axis='y')
    plt.savefig(out_file)


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
            succ = sum(res_slice['success'])
            successes.append(succ)
            fail = n_tries-succ
            perc = 100.0 * float(succ) / float(n_tries)
            f.write('  - {}: {:d}/{:d} = {:.2f}%...{}\n'.format(
                file, succ, fail, perc, 'PASS' if succ else 'FAIL'))
        pd = sum(1 for s in successes if s)
        tt = len(successes)
        fd = tt-pd
        pt = 100.0 * float(pd) / float(tt)
        f.write('\n* and can be summarized as follows:\n')
        f.write('  - PASSED: {0:d}/{1:d} = {2:.2f}%\n'.format(pd, tt, pt))
        f.write('  - FAILED: {0:d}/{1:d} = {2:.2f}%\n'.format(fd, tt, 100-pt))


def fix_ps(log_ps):
    sum_ps = sm.logsumexp(log_ps)
    return [np.exp(p-sum_ps) for p in log_ps]


def test(in_file, out_file, rc):
    pickle_file = os.path.splitext(out_file)[0] + '.pkl'
    if not os.path.exists(pickle_file):
        saveout = sys.stdout
        saveerr = sys.stderr
        file = open(out_file, 'w', 1)
        sys.stdout = file
        sys.stderr = file

        g_trs, _ = parser.load_source(rc.gen_theory)
        e_trs, _ = parser.load_source(in_file, signature=g_trs.signature.copy())
        start = A.App(g_trs.signature.find(rc.start_string), [])

        def test(sampler):
            return sampler.samples_yielded > rc.n_steps or \
                e_trs.unifies(sampler.current_sample.value, type='alpha')

        print '# Generating Theory:\n# {}\n#'.format(
            str(g_trs).replace('\n', '\n# '))
        print '#'
        print '# Evaluating Theory:\n# {}\n#'.format(
            str(e_trs).replace('\n', '\n# '))

        hyps_start = time.time()
        hyps = ss.standard_sample(
            make_hypothesis_maker(rc.p_observe, rc.p_similar,
                                  rc.p_operator, rc.p_arity,
                                  rc.p_rule, start, rc.p_r),
            make_data_maker(e_trs, g_trs, rc.n_changed, rc.n_total,
                            rc.start_string),
            save_top=None, show_skip=0, trace=False, N=10, test=test,
            clean=False, likelihood_temperature=0.5)
        hyps_end = time.time()

        print '\n\n# The best hypotheses of', rc.n_steps, 'samples:'
        for hyp in hyps.get_all(sorted=True):
            print '#'
            print '#', hyp.prior, hyp.likelihood, hyp.posterior_score
            print '# ' + str(hyp).replace('\n', '\n# ')

        print 'Total elapsed time: {:.2f}s'.format(hyps_end-hyps_start)

        sys.stdout = saveout
        sys.stderr = saveerr
        file.close()
        success = any(e_trs.unifies(hyp.value, type='alpha')
                      for hyp in hyps.get_all())
        with open(pickle_file, 'wb') as pkl:
            pickle.dump((in_file, success), pkl)
        return (in_file, success)
    else:
        with open(pickle_file, 'rb') as pkl:
            return pickle.load(pkl)


def make_data_maker(e_trs, g_trs, nChanged, nTotal, start_string):
    def make_data():
        data = TRS.TRS()
        data.signature = e_trs.signature.copy()
        data.signature.parent = data
        start = A.App(g_trs.signature.find(start_string), [])

        print '#'
        print '# Generating data from start symbol:', start.pretty_print()
        lhs_start = time.time()
        trace = start.rewrite(g_trs, max_steps=11,
                              type='all', trace=True)
        lhs_end = time.time()
        states = trace.root.leaves(states=['normal'])
        terms = [s.term for s in states]
        log_ps = [s.log_p*0.5 for s in states]
        ps = fix_ps(log_ps)
        print '# {:d} LHSs generated in {:.2f}s'.format(
            len(terms),
            lhs_end-lhs_start)

        rhs_start = time.time()
        tries = 0
        while data.num_rules() < nTotal:
            tries += 1
            lhs = np.random.choice(terms, p=ps)
            rhs = lhs.rewrite(e_trs, max_steps=7, type='one')
            rule = R.Rule(lhs, rhs)
            if (rule not in e_trs) and \
               ((data.num_rules() < nChanged and lhs != rhs) or
                (data.num_rules() >= nChanged and lhs == rhs) or
                (tries > len(terms)*0.1)):
                data.add(rule)
        rhs_end = time.time()
        print '# {:d} rules selected in {:.2f}s and {:d} tries'.format(
            data.num_rules(),
            rhs_end-rhs_start,
            tries)
        return list(data.rules())

    return make_data


def make_hypothesis_maker(p_observe, p_similar, p_operator, p_arity,
                          p_rule, start, p_r):
    def make_hypothesis(data):
        hyp = TRS.TRS()
        for rule in data:
            for op in rule.operators:
                hyp.signature.add(op)
        return TRSH.TRSHypothesis(value=hyp,
                                  data=data,
                                  privileged_ops=hyp.signature.operators,
                                  p_observe=p_observe,
                                  p_similar=p_similar,
                                  p_operators=p_operator,
                                  p_arity=p_arity,
                                  p_rules=p_rule,
                                  start=start,
                                  p_r=p_r)
    return make_hypothesis


if __name__ == '__main__':
    n = 1600 if len(sys.argv) < 2 else int(sys.argv[1])
    default_filename = 'lib/simple_tree_manipulations/001.terf'
    filename = default_filename if len(sys.argv) < 3 else sys.argv[2]
    start = 'tree' if len(sys.argv) < 4 else sys.argv[3]
    fn, found_it = test(n, filename, start, 4, 'test_log_test')
    print 'tested: {} and {}ed'.format(fn, 'pass' if found_it else 'fail')

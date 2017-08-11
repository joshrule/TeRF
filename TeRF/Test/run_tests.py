import collections
import itertools as iter
import joblib
import LOTlib.Inference.Samplers.StandardSample as ss
import numpy as np
import os
import re
import scipy.misc as sm
import sys
import TeRF.Language.parser as p
import TeRF.Learning.TRSHypothesis as TRSH
import TeRF.Types.Application as A
import TeRF.Types.Rule as R
import TeRF.Types.TRS as TRS
import time


def main(problem_dir, out_dir, n_problems, gen_theory, start,
         n_chains=3, n_steps=3200):
    print '='*80
    print 'It Begins'
    print '='*80 + '\n'
    problems = choose_problems(problem_dir, n_problems)
    report_results(run_tests(problems, out_dir, gen_theory, start,
                             n_chains, n_steps))


def choose_problems(problem_dir, n_problems):
    problems, ps = list_problems(problem_dir)
    problems = np.random.choice(problems, replace=False, size=n_problems, p=ps)
    print '='*80
    print 'Selected Test Problems'
    print '='*80 + '\n'
    for i, prob in enumerate(problems):
        print '{:d}: {}'.format(i, prob)
        trs, _ = p.load_source(prob)
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


def run_tests(problems, out_dir, gen_theory, start, n_chains, n_steps):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    roots = [os.path.splitext(os.path.basename(p))[0] for p in problems]
    for r in roots:
        if not os.path.exists(os.path.join(out_dir, r)):
            os.mkdir(os.path.join(out_dir, r))
    return joblib.Parallel(n_jobs=-1)(
        joblib.delayed(test)(n_steps, p, gen_theory, start,
                             os.path.join(out_dir, r, str(c) + '.log'))
        for (p, r) in iter.izip(problems, roots) for c in xrange(n_chains))


def report_results(results):
    print '='*80
    print 'test results:'
    print '='*80 + '\n'
    res_dict = collections.defaultdict(list)
    for r in results:
        key = r[0]
        res_dict[key].append(r[1])
    for r in res_dict:
        succ = sum(res_dict[r])
        fail = len(res_dict[r])-succ
        perc = 100*succ/(succ+fail)
        print '{}: {:d}/{:d} = {:.2f}%...{}'.format(r, succ, fail, perc,
                                                    'PASS' if succ else 'FAIL')
    pd = sum(any(res_dict[r]) for r in res_dict)
    tt = len(res_dict)
    fd = tt-pd
    pt = 100.0*pd/tt
    print '='*80
    print ('Summary: {0:d}/{3:d} = {2:.2f}% PASS, ' +
           '{1:d}/{3:d} = {4:.2f}% FAIL').format(pd, fd, pt, tt, 100.0-pt)
    print '='*80 + '\n'


def fix_ps(log_ps):
    sum_ps = sm.logsumexp(log_ps)
    return [np.exp(p-sum_ps) for p in log_ps]


def test(n, in_file, gen_theory, start_string, out_file):
    saveout = sys.stdout
    saveerr = sys.stderr
    file = open(out_file, 'w', 1)
    sys.stdout = file
    sys.stderr = file

    g_trs, _ = p.load_source(gen_theory)
    e_trs, _ = p.load_source(in_file, signature=g_trs.signature.copy())
    start = A.App(g_trs.signature.find(start_string), [])

    print '# Generating Theory:\n# {}\n#'.format(
        str(g_trs).replace('\n', '\n# '))
    print '#'
    print '# Evaluating Theory:\n# {}\n#'.format(
        str(e_trs).replace('\n', '\n# '))

    def make_data_maker(nChanged=10, nTotal=20):
        def make_data():
            data = TRS.TRS()
            data.signature = e_trs.signature.copy()
            data.signature.parent = data

            print '#'
            print '# Start symbol:', start.pretty_print()
            lhs_start = time.time()
            trace = start.rewrite(g_trs, max_steps=11, type='all', trace=True)
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
                # print 'rule', rule
                # print 'rule in e_trs', rule in e_trs
                # print 'lhs == rhs', lhs == rhs
                # print '# rules < nChanged', data.num_rules() < nChanged
                if (rule not in e_trs) and \
                   ((data.num_rules() < nChanged and lhs != rhs) or
                    (data.num_rules() >= nChanged and lhs == rhs) or
                    (tries > len(terms)*0.1)):
                    # print 'adding', rule
                    data.add(rule)
            rhs_end = time.time()
            print '# {:d} rules selected in {:.2f}s and {:d} tries'.format(
                data.num_rules(),
                rhs_end-rhs_start,
                tries)
            return list(data.rules())

        return make_data

    def make_hypothesis(data):
        hyp = TRS.TRS()
        for rule in data:
            for op in rule.operators:
                hyp.signature.add(op)
        return TRSH.TRSHypothesis(value=hyp,
                                  data=data,
                                  privileged_ops={s for s in hyp.signature},
                                  p_observe=0.1,
                                  p_similar=0.99,
                                  p_operators=0.5,
                                  p_arity=0.9,
                                  p_rules=0.5,
                                  start=start,
                                  p_r=0.3)

    hyps_start = time.time()
    hyps = ss.standard_sample(make_hypothesis,
                              make_data_maker(nChanged=20, nTotal=40),
                              save_top=None, show_skip=0, trace=False, N=10,
                              steps=n, clean=False, likelihood_temperature=0.5)
    hyps_end = time.time()

    print '\n\n# The best hypotheses of', n, 'samples:'
    for hyp in hyps.get_all(sorted=True):
        print '#'
        print '#', hyp.prior, hyp.likelihood, hyp.posterior_score
        print '# ' + str(hyp).replace('\n', '\n# ')

    print 'samples were generated in {:.2f}s'.format(hyps_end-hyps_start)

    # for hyp in hyps.get_all():
    #     print 'hyp:'
    #     print hyp.value
    #     print 'e_trs:'
    #     print e_trs
    #     print 'equal?', e_trs == hyp.value
    #     print 'sigs?', e_trs.signature == hyp.value.signature
    #     print 'rules?', list(e_trs.rules()) == list(hyp.value.rules())

    sys.stdout = saveout
    sys.stderr = saveerr
    return (in_file, any(e_trs.unifies(hyp.value, type='alpha')
                         for hyp in hyps.get_all()))


if __name__ == '__main__':
    n = 1600 if len(sys.argv) < 2 else int(sys.argv[1])
    default_filename = 'lib/simple_tree_manipulations/001.terf'
    filename = default_filename if len(sys.argv) < 3 else sys.argv[2]
    start = 'tree' if len(sys.argv) < 4 else sys.argv[3]
    fn, found_it = test(n, filename, start, 4, 'test_log_test')
    print 'tested: {} and {}ed'.format(fn, 'pass' if found_it else 'fail')

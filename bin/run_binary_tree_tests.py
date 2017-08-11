#!/usr/bin/env python

import TeRF.Test.run_tests as rt
import sys

problem_dir = 'lib/tests/enumerated/'
gen_theory = 'lib/tests/simple_tree.terf'
start = 'tree'

if len(sys.argv) != 5:
    print 'usage: run_binary_tree_tests.py ' + \
        '<out_dir> <n_problems> <n_chains> <n_steps>'
else:
    out_dir = sys.argv[1]
    n_problems = int(sys.argv[2])
    n_chains = int(sys.argv[3])
    n_steps = int(sys.argv[4])

    rt.main(problem_dir, out_dir, n_problems, gen_theory, start,
            n_chains=n_chains, n_steps=n_steps)

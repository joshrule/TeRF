#!/usr/bin/env python

import TeRF.Test.run_tests as rt
import sys

if len(sys.argv) != 2:
    print 'usage: run_binary_tree_tests.py <rcfile>'
else:
    rt.sample_main(sys.argv[1])

#!/usr/bin/env python

import TeRF.Test.make_tests as mt
import TeRF.Types.Operator as O
import TeRF.Types.Signature as S
import sys

if len(sys.argv) != 3:
    print 'usage: make_binary_tree_tests.py <out_dir> <max_nodes>'
else:
    out_dir = sys.argv[1]

    max_nodes = sys.argv[2]

    a = O.Op('A', 0)
    b = O.Op('B', 0)
    c = O.Op('C', 0)
    app = O.Op('.', 2)
    sig = S.Signature({a, b, c, app})

    mt.make_tests(out_dir, sig, int(max_nodes))

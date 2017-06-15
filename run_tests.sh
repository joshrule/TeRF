#!/bin/bash

import="import TeRF.Hypotheses.TRSHypothesis as t ; "

for i in `seq -w 1 33`;
do
    logfile="test_log_1600_0$i"
    testfile="'./tests/0$i.terf'"
    cmd="{ time python -c \"$import t.test(1600, $testfile)\" ; } &> $logfile"
    eval $cmd
    echo $i
done

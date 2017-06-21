#!/bin/bash

import="import TeRF.Hypotheses.TRSHypothesis as t ; "
nSamps="1600"

for i in `seq -w 1 33`;
do
    logfile="test_log_$nSamps\_0$i\_25_50_3"
    testfile="'./tests/0$i.terf'"
    cmd="{ time python -c \"$import t.test($nSamps, $testfile)\" ; } &> $logfile"
    eval $cmd
    echo $i
done

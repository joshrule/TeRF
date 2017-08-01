#!/bin/bash

import="import TeRF.Hypotheses.TRSHypothesis as t ; "
nSamps="3200"
today=`date '+%Y%m%d'`

for i in `seq -f %03g 21 32`;
do
    logfile=test_log_${nSamps}_${i}_20_40_3
    testfile=library/simple_tree_manipulations/${i}.terf
    echo Next Test $i: $testfile
    read -p "Run this test (<y>|n)? " runit
    if [[ $runit == '' ]] || [[ $runit == 'y' ]]
    then
        script $logfile bin/test.sh $nSamps $testfile $start
    else
        echo skipping test
    fi
done

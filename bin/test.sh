i=$1
nSamps=$2
start=$3
n=$4
testfile=lib/simple_tree_manipulations/${i}.terf
# today=`date '+%Y%m%d'`
logfile=test_log_${nSamps}_${i}_20_40_${n}

echo test $i: $testfile
(time python TeRF/Learning/TRSHypothesis.py $nSamps $testfile $start) \
    &> $logfile

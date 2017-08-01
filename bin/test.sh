i=$1
nSamps=$2
start=$3
n=$4
testfile=library/simple_tree_manipulations/${i}.terf
today=`date '+%Y%m%d'`
logfile=test_log_${nSamps}_${i}_20_40_${n}

echo Next Test $i: $testfile
read -p "Run this test (<y>|n)? " runit
if [[ $runit == '' ]] || [[ $runit == 'y' ]]
then
    script $logfile time python TeRF/Learning/TRSHypothesis.py $nSamps \
           $testfile $start
else
    echo skipping test
fi

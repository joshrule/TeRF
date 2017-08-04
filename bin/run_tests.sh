#!/bin/bash

for i in `seq -f %03g 1 32`;
do
    bin/test.sh $i $1 $2 $3
done

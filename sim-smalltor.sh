#!/bin/sh
NUM_RUNS=1000
MAX_EVENTS=2000000



for((d=10;d<100;d*=2)); do
    rm conv-smalltor-$d.txt
    echo "smalltor, all to random, ecmp, degree $d"
    echo "running $NUM_RUNS simulations for degree $d"
    for((i=1;i<=$NUM_RUNS;i+=1)); do python frugal1_test.py --cap ../mpsim/smalltor-cap.txt --tm ../mpsim/smalltor-a2rsde-$i-$d.txt --ev $MAX_EVENTS > smalltor-a2rsde-$i-$d-out.txt ; done
    echo "number of cases that converged, out of $NUM_RUNS"
    for((s=1;s<=9;s+=1)); do
         grep converge smalltor-a2rsde-$s*-$d-out.txt | grep -v not >> conv-smalltor-$d.txt;
    done
    wc -l conv-smalltor-$d.txt

    echo "cases that didn't converge for smalltor-a2rsde-x-$d-out.txt"
    cat conv-smalltor-$d.txt | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk 'BEGIN{prev = 0;} {if ($1 > prev+1) {print prev+1;} prev=$1;}' | xargs -I_index grep -v "No flows" smalltor-a2rsde-_index-$d-out.txt /dev/null
done
#!/bin/sh
NUM_RUNS=1000
MAX_EVENTS=2000000



for((d=10;d<100;d*=2)); do
    rm conv-onetor-$d.txt
    echo "onetor, all to random, ecmp, degree $d"
    echo "running $NUM_RUNS simulations for degree $d"
    for((i=1;i<=$NUM_RUNS;i+=1)); do python frugal1_test.py --cap ../mpsim/onetor-cap.txt --tm ../mpsim/onetor-a2rsde-$i-$d.txt --ev $MAX_EVENTS > onetor-a2rsde-$i-$d-out.txt ; done
    echo "number of cases that converged, out of $NUM_RUNS"
    for((s=1;s<=9;s+=1)); do
         grep converge onetor-a2rsde-$s*-$d-out.txt | grep -v not >> conv-onetor-$d.txt;
    done
    wc -l conv-onetor-$d.txt

    echo "cases that didn't converge for onetor-a2rsde-x-$d-out.txt"
    cat conv-onetor-$d.txt | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk 'BEGIN{prev = 0;} {if ($1 > prev+1) {print prev+1;} prev=$1;}' | xargs -I_index grep -v "No flows" onetor-a2rsde-_index-$d-out.txt /dev/null
done
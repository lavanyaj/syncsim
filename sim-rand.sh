#!/bin/sh
NUM_RUNS=1000
MAX_EVENTS=20000000



# for((d=10;d<100;d*=2)); do
#     echo "rand, uniformly distributed path lengths, for 100 vertex topo, for flows per link of $d"
#     echo "running $NUM_RUNS simulations for degree $d"
#     for((i=1;i<=$NUM_RUNS;i+=1)); do python frugal1_test.py --cap ../mpsim-gen/rand-capn-100.txt --tm ../mpsim-gen/rand-tmusfv-$i-$d-100.txt --ev $MAX_EVENTS > rand-tmusfv-$i-$d-100-out.txt ; done
    
#     # echo "cases that didn't converge for pfab-a2rsde-x-$d-out.txt"
#     # cat conv-pfab-$d.txt | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk 'BEGIN{prev = 0;} {if ($1 > prev+1) {print prev+1;} prev=$1;}' | xargs -I_index grep -v "No flows" pfab-a2rsde-_index-$d-out.txt /dev/null
# done

for((d=40;d<100;d*=2)); do
    rm conv-rand-100-$d.txt
    touch conv-rand-100-$d.txt
    echo "number of cases that converged, out of $NUM_RUNS"
    for((s=1;s<=9;s+=1)); do
        grep converge rand-tmusfv-$s*-$d-100-out.txt  >> conv-rand-100-$d.txt;
    done
    wc -l conv-rand-100-$d.txt
done

# for((d=40;d<100;d*=2)); do
#     echo "rand, uniformly distributed path lengths, for 100 vertex topo, for flows per link of $d"
#     echo "running $NUM_RUNS simulations for degree $d"
#     for((i=1;i<=$NUM_RUNS;i+=1)); do python frugal1_test.py --cap ../mpsim-gen/rand-capn-100.txt --tm ../mpsim-gen/rand-tmusfv-$i-$d-100.txt --ev $MAX_EVENTS > rand-tmusfv-$i-$d-100-out.txt ; done
    
    # echo "cases that didn't converge for pfab-a2rsde-x-$d-out.txt"
    # cat conv-pfab-$d.txt | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk -F "-" '{print $3;}' | sort -k1,1 -n | awk 'BEGIN{prev = 0;} {if ($1 > prev+1) {print prev+1;} prev=$1;}' | xargs -I_index grep -v "No flows" pfab-a2rsde-_index-$d-out.txt /dev/null
#done

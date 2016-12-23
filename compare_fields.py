import sys
from itertools import izip

file_1 = sys.argv[1]
file_2 = sys.argv[2]

for line_from_file_1, line_from_file_2 in izip(open(file_1), open(file_2)):
    if not line_from_file_1.startswith("OUT: Flow"):
        continue
    tokens1 = line_from_file_1.rstrip().split()
    tokens2 = line_from_file_2.rstrip().split()

    num_words = len(tokens1)
    assert(len(tokens2) == num_words)
    
    assert(tokens1[1] == "Flow")
    assert(tokens2[1] == "Flow")


    num1 = tokens1[num_words-3]
    rate1 = tokens1[num_words-1]

    num2 = tokens2[num_words-3]
    rate2 = tokens2[num_words-1]

    assert(num1 == num2)
    
    print str(rate1) + " " + str(rate2)
    

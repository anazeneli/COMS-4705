#! /usr/bin/python2.7

__author__="Ana Zeneli <a.zeneli@columbia.edu>"
__date__ ="$Oct 12, 2018"

import os, sys, re, json, itertools
from collections import defaultdict
import time
"""
frequency count should be part of the program, which
means the "cfg.counts" is a temporary file and will be
regenerated every time.
"""

# define globals
q              = {}
wordlist       = {}
nonterminals   = {}
binary         = {}
unary          = {}
high_freq      = {}
b_rules        = {}

# *************************** Q4 *******************************
def get_counts(count) :
    with open(count, 'r') as f:
        for line in f:
            words = line.split()
            if words[1] == 'UNARYRULE':
                if words[3] in wordlist.keys():
                    wordlist[words[3]] += int(words[0])
                else:
                    wordlist[words[3]] = int(words[0])
                if (words[2],words[3]) in unary.keys():
                    unary[words[2],words[3]] += int(words[0])
                else:
                    unary[words[2], words[3]] = int(words[0])

            elif words[1] == 'BINARYRULE':
                binary[words[2], words[3], words[4]] = int(words[0])
                if words[2] in b_rules.keys() :
                    b_rules[words[2]].append([words[3], words[4]])
                else:
                    b_rules[words[2]] = [[words[3], words[4]]]

            elif words[1] == 'NONTERMINAL':
                nonterminals[words[2]] = int(words[0])

    return b_rules, wordlist, nonterminals, unary, binary

# recursively replace words
def replace(tree, token):
    if len(tree) == 2:
        if tree[1] not in high_freq:
            tree[1] = token
    elif len(tree) == 3:
        tree[1] = replace(tree[1], token)
        tree[2] = replace(tree[2], token)
    return tree

def replace_rare(rareFile):
    # create a dictionary of not rare words to
    # keep in place in parser_dev.train
    for i in wordlist:
        if wordlist[i] >= 5:
            high_freq[i] = wordlist[i]

    # recursively walk through the parse tree
    token = "_RARE_"
    with open(trainFile, "r") as f:
        trees = [replace(json.loads(line), token) for line in f]

    with open(rareFile, "w") as outfile:
        for t in trees:
            outfile.write(json.dumps(t) + "\n")
# *************************** Q5 ********************************
# Emissions from the rare words count
def compute_rule_params(count):
    # local lookup is faster than global
    _, _, nonterminals, unary, binary = get_counts(count)
    # q(X -> Y1Y2) = Count(X-> Y1Y2) / Count(X)
    for i,j,k in binary:
        q[i,j,k] = float(binary[i,j,k]) / nonterminals[i]
        # print i,j,k, q[i,j,k]

    # Unary Parameter calculation
    # q(X -> w) = Count(X-> w) / Count(X)
    for i,j in unary:
        q[i, j] = float(unary[i, j]) / nonterminals[i]
        # print i, j, q[i,j]

# dynamic programming algorithm
# takes in a sentence as input and
# returns the highest probability parse
# tree with S as its root
def cky(sen):
    token = "_RARE_"
    n = len(sen)
    #initialize to zero to avoid later key errros
    pi = defaultdict(lambda: 0)
    bp = defaultdict(tuple)
    u_keys = unary.keys()
    b_keys = binary.keys()
    l_rules = b_rules.keys()

    # INITIALIZATION
    for i in range(n):
        for X in nonterminals:
            if sen[i] not in wordlist:
                # Handle rare words in new file
                if (X, token) in u_keys:
                    pi[i,i,X] =  q[X, token]
                    bp[i,i,X] = (sen[i], -1)

            elif (X, sen[i]) in u_keys:
                pi[i,i,X] =  q[X, sen[i]]
                bp[i,i,X] = (sen[i] , -1)

    # ALGORITHM
    for l in range(1,n):
        # i is the index of the array
        for i in range(n-l):
            j = i+l
            for X in l_rules:
                max_pi = 0
                max_bp = ()
                rules = b_rules[X]
                for r in rules:
                    y,z = r
                    split_range = range(i, j)
                    for s in split_range:
                        temp_pi = q[X,y,z] * pi[i,s,y] * pi[s+1, j, z]
                        if temp_pi > max_pi:
                            max_pi = temp_pi
                            # record the rule and split point of max prob
                            max_bp = (y,z, s)

                    pi[i,j,X] = max_pi
                    bp[i,j,X] = max_bp

    if pi[0, n - 1, 'S'] != 0:
        return trace(bp, 0, n - 1, 'S')
    else:
        list = []
        for X in nonterminals:
            list.append( [X, pi[0, n - 1, X]])
        index, value = max(list, key=lambda item: item[1])

        return trace(bp, 0, n - 1, index)

# Recursibely rebuild parse tree using bp
def trace(bp, i,j,x) :
    rootlen= len(bp[i,j,x])
    if rootlen == 2:
        # return the word
        return [x, bp[i,j,x][0]]
    elif rootlen == 3:
        y,z,s = bp[i,j,x]
        return [x, trace(bp, i, s, y), trace(bp, s+1, j, z)]
    else:
        raise ValueError("Invalid rule.")

if __name__ == '__main__':
    start_time = time.time()

    if sys.argv[1] == 'q4':
        # Calculate counts
        trainFile = sys.argv[2]
        rareFile  = sys.argv[3]

        counts = "cfg.counts"
        os.system("python count_cfg_freq.py " + trainFile + ">" + counts)
        get_counts(counts)
        replace_rare(rareFile)

    elif sys.argv[1] == 'q5' or sys.argv[1] == 'q6':
        # run CKY
        rareFile  = sys.argv[2]
        testFile  = sys.argv[3]
        predFile  = sys.argv[4]
        counts    = "cfg.counts_rare"

        # rerun counts using rarefile
        os.system("python count_cfg_freq.py " + rareFile + ">" + counts)
        # get_counts(counts)
        compute_rule_params(counts)

        with open(testFile, "r") as f:
            trees = [line.split() for line in f]

        parsed_trees = map(cky, trees)

        with open(predFile, "w") as outfile:
            for t in parsed_trees:
                outfile.write(json.dumps(t) + '\n')

    else:
        raise ValueError('Enter python parser.py q4/q5/q6 and necessary files ')

    print("--- %s seconds ---" % (time.time() - start_time))

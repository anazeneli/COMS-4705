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
not_rare_words = {}
#initialize to zero to avoid later key errros
pi = defaultdict(lambda: 0)
bp = defaultdict(tuple)

# *************************** Q4 *******************************

def get_counts(count) :
    for line in count:
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
        elif words[1] == 'NONTERMINAL':
            nonterminals[words[2]] = int(words[0])

def replace_rare_words():
    # create a dictionary of not rare words to
    # keep in place in parser_dev.train
    for i in wordlist:
        if wordlist[i] >= 5:
            not_rare_words[i] = wordlist[i]

    # recursively walk through the parse tree
    token = "_RARE_"

    def replace(tree, token):
        if len(tree) == 2:
            if tree[1] not in not_rare_words:
                tree[1] = token
        elif len(tree) == 3:
            tree[1] = replace(tree[1], token)
            tree[2] = replace(tree[2], token)
        return tree

    with open(trainFile) as f:
        trees = map(lambda l: json.loads(l.strip()), f.readlines())

    rare_trees =  map(lambda l: replace(l, token), trees)

    with open("parse_train.RARE.dat", "w") as outfile:
        str = map(lambda t: json.dumps(t), rare_trees)
        outfile.write('\n'.join(str))

# *************************** Q5 ********************************
# Emissions from the rare words count
def compute_rule_params():
    # q(X -> Y1Y2) = Count(X-> Y1Y2) / Count(X)
    for i,j,k in binary:
        q[i,j,k] = float(binary[i,j,k]) / nonterminals[i]
        # print i,j,k, q[i,j,k]

    # Unary Parameter calculation
    # q(X -> w) = Count(X-> w) / Count(X)
    for i,j in unary:
        q[i, j] = float(unary[i, j]) / nonterminals[i]
        # print i, j, q[i,j]

# cky algorithm takes a sentence and
# returns the highest probability parse
# tree with S as its root
def cky(sen):
    n = len(sen)
    # INITIALIZATION
    for i in range(n):
        for X in nonterminals:
            if sen[i] not in wordlist:
                # Handle rare words in new file
                token = "_RARE_"
                if (X, token) in unary.keys():
                    pi[i,i,X] =  q[X, token]
                    bp[i,i,X] = (sen[i], -1)

            elif (X, sen[i]) in unary.keys():
                pi[i,i,X] =  q[X, sen[i]]
                bp[i,i,X] = (sen[i] , -1)

    # ALGORITHM
    for l in range(1,n):
        # i is the index of the array
        for i in range(n-l):
            j = i+l
            for X in nonterminals:
                max_pi = 0
                max_bp = ()

                split_range = range(i, j)
                for s in split_range:
                    for x,y,z in binary.keys():
                        if x == X:
                            temp_pi = q[x,y,z] * pi[i,s,y] * pi[s+1, j, z]
                            if temp_pi > max_pi:
                                max_pi = temp_pi
                                # record the rule and split point of max prob
                                max_bp = (y,z, s)

                    pi[i,j,X] = max_pi
                    bp[i,j,X] = max_bp

    # fix issues that arise from sentence fragment
    # submit the value of the highest parse
    # using indices of first and final element
    root = ''
    if pi[0,n-1,'S'] != 0:
        return trace(0, n-1, 'S')
    # else sentence is a fragment, choose a new root value
    else:
        list = []
        for X in nonterminals:
            list.append([X, float(pi[0,n-1, X])])

        index, value = max(list, key=lambda item: item[1])
        # print index, value
        return trace(0, n-1, index)

# Rebuild parse tree using bp
def trace(i,j,x) :
    rootlen= len(bp[i,j,x])

    if rootlen == 2:
        # return the word
        return [x, bp[i,j,x][0]]
    elif rootlen == 3:
        y,z,s = bp[i,j,x]
        return [x, trace(i, s, y), trace(s+1, j, z)]

if __name__ == '__main__':
    if sys.argv[1] == 'q4':
        # Calculate counts
        trainFile = sys.argv[2]
        rareFile  = sys.argv[3]

        counts = "cfg.counts"
        os.system("python count_cfg_freq.py " + trainFile + ">" + counts)
        countOpen=open(counts,'r')
        get_counts(countOpen)
        replace_rare_words()
    elif sys.argv[1] == 'q5':
        start_time = time.time()
        # run CKY
        rareFile  = sys.argv[2]
        testFile  = sys.argv[3]
        predFile  = sys.argv[4]
        counts    = "cfg.counts_rare"

        # rerun counts using rarefile
        os.system("python count_cfg_freq.py " + rareFile + ">" + counts)
        countOpen=open(counts,'r')
        get_counts(countOpen)
        compute_rule_params()

        # read in test file
        trees = []
        with open(testFile) as f:
            for line in f:
                t = line.split()
                trees.append(t)

        parsed = []
        for t in trees:
            parsed.append(cky(t))

        with open(predFile, "w") as outfile:
            str = map(lambda t: json.dumps(t), parsed)
            outfile.write('\n'.join(str))

        print("--- %s seconds ---" % (time.time() - start_time))

    elif sys.argv[1] == 'q6':
        # efficiency test
        raise ValueError('NOt yet setup')

    else:
        raise ValueError('Enter python parser.py q4/q5/q6 and necessary files ')

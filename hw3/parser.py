#! /usr/bin/python2.7

__author__="Ana Zeneli <a.zeneli@columbia.edu>"
__date__ ="$Oct 12, 2018"

import os, sys, re, json, itertools
from rare_words_preprocessor import *

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
    pi = {}
    bp = {}
    # INITIALIZATION
    for i in range(n):
        for X in nonterminals:
            if (X, sen[i]) in unary.keys():
                pi[i,i,X] = q[X, sen[i]]
            else:
                pi[i,i,X] = 0

    # ALGORITHM
    for l in range(1, n-1):
        # i is the index of the array
        for i in range(n-l):
            j = i+l
            for X in nonterminals:
                max_pi = 0
                max_bp = ()
                for x,y,z in binary.keys():
                    if x == X:
                        split_range = range(i, j)
                        for s in split_range:
                            if (i,s,y) in pi.keys() and (s+1,j, z) in pi.keys():
                                temp_pi = q[x,y,z] * pi[i,s,y] * pi[s+1, j, z]
                            else:
                                temp_pi = 0
                            if temp_pi > max_pi:
                                max_pi = temp_pi
                                # record the rule and split point of max prob
                                max_bp = ((y,z), s)

                            pi[i,j,X] = max_pi
                            bp[i,j,X] = max_bp

    # fix sentence fragment issues
    # if pi[0,n-1,'S'] != 0:
    #     return pi[0,n-1,'S']
    # else:
    #     max_pi = 0
    #     max_X = ''
    #     for X in nonterminals:
    #         if (0,n-1,X) not in pi.keys():
    #             temp_pi = pi[0,n-1,X]
    #         else:
    #             temp_pi = 0
    #
    #         if temp_pi > max_pi:
    #             max_pi  = temp_pi
    #             max_X = X
    #
    #     return pi[1,n-1,max_X]

if __name__ == '__main__':
    if sys.argv[1] == 'q4':
        # Calculate counts
        trainFile = sys.argv[2]
        rareFile  = sys.argv[3]
        counts    = "cfg.counts"

        rw = RareWordsPreprocessor(trainFile, rareFile, counts)

    elif sys.argv[1] == 'q5':
        # run CKY
        rareFile  = sys.argv[2]
        testFile   = sys.argv[3]
        predFile  = sys.argv[4]
        counts    = "cfg.counts_rare"
        rw = RareWordsPreprocessor(rareFile, testFile, counts)

        compute_rule_params()

        trees = []
        with open(testFile) as f:
            for line in f:
                t = line.split()
                trees.append(t)

        for t in trees:
            cky(t)
        raise ValueError('NOt yet setup')

    elif sys.argv[1] == 'q6':
        # efficiency test
        raise ValueError('NOt yet setup')

    else:
        raise ValueError('Enter python parser.py q4/q5/q6 and necessary files ')

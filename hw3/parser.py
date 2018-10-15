#! /usr/bin/python2.7

__author__="Ana Zeneli <a.zeneli@columbia.edu>"
__date__ ="$Oct 12, 2018"

import os, sys, re, json, itertools
"""
frequency count should be part of the program, which
means the "cfg.counts" is a temporary file and will be
regenerated every time.
"""

# Calculate counts
trainFile = "parse_train.dat"
rareFile = "parse_train.RARE.dat"
os.system("python count_cfg_freq.py " + trainFile + "> cfg.counts")
countOpen=open('cfg.counts','r')

q = {}
tokenlist      = {}
nonterminals   = {}
binary         = {}
unary          = {}
not_rare_words = {}

def get_counts(count) :
    for line in count:
        words = line.split()
        if words[1] == 'UNARYRULE':
            if words[3] in tokenlist.keys():
                tokenlist[words[3]] += int(words[0])
            else:
                tokenlist[words[3]] = int(words[0])
            if (words[2],words[3]) in unary.keys():
                unary[words[2],words[3]] += int(words[0])
            else:
                unary[words[2], words[3]] = int(words[0])

        elif words[1] == 'BINARYRULE':
            binary[words[2], words[3], words[4]] = int(words[0])
        elif words[1] == 'NONTERMINAL':
            nonterminals[words[2]] = int(words[0])

# create a dictionary of rare words to replace in oarser_dev.train
for i in tokenlist:
    if tokenlist[i] >= 5:
        not_rare_words[i] = tokenlist[i]


def replace_rare_words():
    token = "_RARE_"

    # recursively walk through the parse tree
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

    with open(rareFile, "w") as outfile:
        str = map(lambda t: json.dumps(t), rare_trees)
        outfile.write('\n'.join(str))

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
    for i in range(1, n):
        for X in nonterminals:
            if  X == 'S':
                if (X, sen[i]) in unary.keys():
                    pi[i,i,X] = q[X, sen[i]]
                else:
                    pi[i,i,X] = 0

    # ALGORITHM
    for l in range(1, n-1):
        for i in range(1,n-l):
            j = i+l
            for X in nonterminals:
                for x,y,z in binary.keys():
                    max_pi = 0
                    max_bp = ()
                    if x == X:
                        split_range = range(i, j-1)
                        for s in split_range:
                            temp_pi = q[x,y,z] * pi[i,s,y] * pi[s+1, j, z]

                            if temp_pi > max_pi:
                                max_pi = pi
                                max_bp = ([x,y,z], s)

                        pi[i,j,X] = max_pi
                        bp[i,j,X] = max_bp

    # fix sentence fragment issue
    if pi[1,n,'S'] != 0:
        return pi[1,n,'S']
    else:
        max_pi = 0
        max_X = ''
        for X in nonterminals:
            temp_pi = pi[1,n,X]

            if temp_pi > max_pi:
                max_pi  = temp_pi
                max_X = X

        return pi[1,n,max_X]


if __name__ == '__main__':
    get_counts(countOpen)
    replace_rare_words()

    os.system("python count_cfg_freq.py " + rareFile + "> cfg.counts_rare")
    rareCountOpen=open('cfg.counts_rare','r')

    get_counts(rareCountOpen)
    compute_rule_params()

    testFile = "parse_dev.dat"
    trees = []
    with open(testFile) as f:
        for line in f:
            t = line.split()
            trees.append(t)

    for t in trees:
        cky(t)

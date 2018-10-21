#! /usr/bin/python2.7

__author__="Ana Zeneli <a.zeneli@columbia.edu>"
__date__ ="$Oct 12, 2018"

import os, sys, re, json, itertools
from collections import defaultdict
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


def get_counts(self, count) :
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

    with open("parse_train_RARE.dat", "w") as outfile:
        str = map(lambda t: json.dumps(t), rare_trees)
        outfile.write('\n'.join(str))





if __name__ == '__main__':
    if sys.argv[1] == 'q4':
        # Calculate counts
        trainFile = sys.argv[2]
        rareFile  = sys.argv[3]

        counts = "cfg.counts"
        os.system("python count_cfg_freq.py " + trainFile + ">" + counts)
        countOpen=open(counts,'r')
        get_counts()
        replace_rare_words()
    elif sys.argv[1] == 'q5':
        # run CKY
        rareFile  = sys.argv[2]
        testFile  = sys.argv[3]
        predFile  = sys.argv[4]
        counts    = "cfg.counts_rare"

        # rerun counts using rarefile
        os.system("python count_cfg_freq.py " + rareFile + ">" + counts)
        countOpen=open(counts,'r')
        get_counts()
        compute_rule_params()

        # read in test file
        trees = []
        with open(testFile) as f:
            for line in f:
                t = line.split()
                trees.append(t)

        for t in trees:
            cky(t)

    elif sys.argv[1] == 'q6':
        # efficiency test
        raise ValueError('NOt yet setup')

    else:
        raise ValueError('Enter python parser.py q4/q5/q6 and necessary files ')

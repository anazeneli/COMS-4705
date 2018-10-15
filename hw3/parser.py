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

tokenlist  = {}
not_rare_words = {}
for line in countOpen:
    words = line.split()
    if words[1] == 'UNARYRULE':
        if words[3] in tokenlist.keys():
            tokenlist[words[3]] += int(words[0])
        else:
            tokenlist[words[3]] = int(words[0])

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

replace_rare_words()

os.system("python count_cfg_freq.py " + rareFile + "> cfg.counts_rare")
rareCountOpen=open('cfg.counts_rare','r')

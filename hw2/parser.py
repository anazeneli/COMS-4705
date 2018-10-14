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

# create a dictionary of rare words to replace in parser_dev.train
for i in tokenlist:
    if tokenlist[i] >= 5:
        not_rare_words[i] = tokenlist[i]

def replace_rare_words(d, token):
    token = "_RARE_"
    with open(trainFile) as f:
        trees = map(lambda l: json.loads(l.strip()), f.readlines())

    count = 0
    for t in trees:
        count += 1
        if count <= 10:
            print t
            for i in range(1,len(t)):
                # print i, t[i], len(t[i])
                for j in range(1, len(t[i])):
                    if len(t[i][j]) == 2:
                        word = t[i][j][1]
                        # if not in dict, replace rare word
                        print "UNARY"
                        print word
                        if word not in d.keys():
                            t[i][j][1] = token
                        # print "UNARY", t[i][j][1]
                    elif len(t[i][j]) == 3:
                        w1 = t[i][j][1][1]
                        w2 = t[i][j][2][1]
                        print w1
                        print w2
                        if w1 not in d.keys():
                            t[i][j][1][1] = token
                        if w2 not in d.keys():
                            t[i][j][2][1] = token

                        # print "BINARY RULE", t[i][j][k][1]


    with open("rare_words.dat", "w") as outfile:
        str = map(lambda t: json.dumps(t), trees)
        outfile.write('\n'.join(str))


replace_rare_words(not_rare_words, "_RARE_")

import os, sys, re, json, itertools

"""
frequency count should be part of the program, which
means the "cfg.counts" is a temporary file and will be
regenerated every time.
"""

# define globals
wordlist      = {}
nonterminals   = {}
binary         = {}
unary          = {}
not_rare_words = {}

class RareWordsPreprocessor():
    def __init__(self, f1, f2, counts):
        self.trainFile = f1
        self.rareFile = f2

        os.system("python count_cfg_freq.py " + self.trainFile + "> " + counts )
        countOpen= open(counts,'r')
        self.get_counts(countOpen)

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

    # create a dictionary of rare words to replace in oarser_dev.train
    for i in wordlist:
        if wordlist[i] >= 5:
            not_rare_words[i] = wordlist[i]

    def replace_rare_words(self):
        token = "_RARE_"
        trainFile = self.trainFile
        rareFile  = self.rareFile
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

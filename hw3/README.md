PCFG Parser using CKY algorithm. 

Question 4
Execution:
    python parser.py q4 parse_train.dat parse_train.RARE.dat

Question 5
Execution:
    python parser.py q5 parse_train.RARE.dat parse_dev.dat q5_prediction_file
    python eval_parser.py parse_dev.key q5_prediction_file > q5_eval.txt

Observations:
    The parser worked best for simpler tags, like ., ADP, and DET, and for tags with less ambiguity, like NP+PRON and NOUN. The parser performed relatively poorly with S assignment, but again this can be attributed to ambiguity, as some sentences were fragments. Ensuring to use "_RARE_" in place of unseen words protects against pi=0 too frequently.

Question 6
Execution:
    python parser.py q4 parse_train_vert.dat parse_train_vert.RARE.dat
    python parser.py q6 parse_train_vert.RARE.dat parse_dev.dat q6_prediction_file
    python eval_parser.py parse_dev.key q6_prediction_file > q6_eval.txt

Observations:
    Efficiency of algorithm greatly improved once I hashed X -> YZ, using X as the rule lookup, and adding YZ to a list as the value. This reduced the time from initially well over 200 seconds to 40 seconds in part 5, and from 400 to 96 in part 6. 
    
   The performance of the parser using vertical markovization is 0.742-- a 0.028 improvement over the baseline parser. With vector markovization, we see the same totals, but with a higher precision, recall and f1 score. With a higher contextual accuracy, the parser can more correctly assign tags. We see an improvement even in the low count tags like NP+ADJ and NP+NUM.

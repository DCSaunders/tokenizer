import argparse
import numpy as np
import collections
import sys
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delimit_grammar', default='//', help='Grammar rule delimiter')
    parser.add_argument('-u', '--UNK', default='UNK ==> UNK', help='unknown symbol')
    parser.add_argument('-ut', '--TERMINAL_UNK', default='<unk>')
    parser.add_argument('-w', '--wmap_in', help='Location to load wmap')
    parser.add_argument('-o', '--out_idx', default=None, help='Location to save mapped out')
    parser.add_argument('-i2g', '--to_grammar', default=False, 
                        action='store_true', help='True if idx->rules')
    parser.add_argument('-i2w', '--to_words', default=False, 
                        action='store_true', help='True if idx->words')

    return parser.parse_args()

ambig_terminals = set(['-RRB', '-LRB', 'N'])

def is_terminal(tok, nt, nt_list):
    if tok not in nt_list:
        return True
    else:
        if ((tok.lower() == tok and nt.lower() == nt) or
            (nt in ambig_terminals and tok in ambig_terminals)):
            return True
    return False


def mapped_prod(prod, rule_map, nt_set):
    if args.to_words:
        lhs, rhs = rule_map[prod].split('==>')
        lhs = lhs.strip()
        rhs_split = rhs.strip().split()
        if len(rhs_split) == 1 and is_terminal(rhs_split[0], lhs, nt_set):
            return rhs_split[0]
        else:
            return ''
    else:
        return rule_map[prod]

def unk_or_unk_t(prod, rule_map, out, nt_set):
    lhs, rhs = prod.split(' ==> ')
    rhs_split = rhs.split()
    if len(rhs_split) == 1 and is_terminal(rhs_split[0], lhs, nt_set):
        out.append(rule_map['{} ==> {}'.format(lhs, args.TERMINAL_UNK)])
    else:
        out.append(rule_map[args.UNK])


args = get_args()
rule_map = {}
nt_set = set()
with open(args.wmap_in, 'r') as f:
    for line in f:
        split = line.split()
        rule_map[' '.join(split[:-1])] = split[-1]
        nt_set.add(split[0])

if args.to_words or args.to_grammar:
    rule_map = {v : k for k, v in rule_map.items()}
    joiner = ' {} '.format(args.delimit_grammar) if args.to_grammar else ' '
    delimiter = ' '
else:
    joiner = ' '
    delimiter = args.delimit_grammar

def get_out_line(line):
    line = line.strip().strip(joiner)
    productions = line.split(delimiter)
    out = []
    for prod in productions:
        prod = prod.strip()
        if prod in rule_map:
            out.append(mapped_prod(prod, rule_map, nt_set))
        elif prod:
            unk_or_unk_t(prod, rule_map, out, nt_set)
    return out

if args.out_idx:
    with open(args.out_idx, 'w') as f:
        for line in sys.stdin:
            out = get_out_line(line)
            f.write('{}\n'.format(joiner.join(out)))
else:
    for line in sys.stdin:
        sys.stdout.write('{}\n'.format(joiner.join(get_out_line(line))))
    

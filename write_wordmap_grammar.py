import argparse
import numpy as np
import collections
import re
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vocab_size', type=int, default=0, help='Vocab size for wmap, 0 if whole vocab')
    parser.add_argument('-s', '--split_grammar', default='==>', help='Grammar rule delineator')
    parser.add_argument('-w', '--wmap_out', default='/tmp/wmap', help='Location to save new wmap')
    parser.add_argument('-o', '--grammar_out', default='/tmp/grammar', help='Location to save mapped grammar')
    return parser.parse_args()

def output_rule(nt, rules, ids, wmap_idx, f, f_w):
    for rule_rhs in rules[nt]:
        rule_out = []
        for r in rule_rhs:
            if len(rule_rhs) == 1 and r == nt and r not in (eps, unk):
                # some terminals are identical to non-terminals e.g. '.'
                r = '{}-T'.format(r) 
            if r not in ids:
                ids[r] = str(len(ids))
            rule_out.append(ids[r])
        f.write('{} : {}\n'.format(ids[nt], ' '.join(rule_out)))
        f_w.write('{} {} {} {}\n'.format(
        nt, args.split_grammar, ' '.join(rule_rhs), wmap_idx))
        wmap_idx += 1
    return wmap_idx

eps = '<epsilon>'
unk = 'UNK'
args = get_args()
rules = collections.defaultdict(list) # maps nt to list of split RHSs
ids = {eps: '0', unk: '1'}
for line in sys.stdin:
    lhs, rhs = line.strip('\n').split(args.split_grammar)
    rules[lhs.strip()].append(rhs.split())

for idx, nt in enumerate(rules, start=2):
    ids[nt] = str(idx)
rules[eps].append([eps])
rules[unk].append([unk])

with open(args.grammar_out, 'w') as f, open(args.wmap_out, 'w') as f_w:
    output_rule(eps, rules, ids, 0, f, f_w)
    output_rule(unk, rules, ids, 1, f, f_w)
    wmap_idx = 2
    rules.pop(eps)
    rules.pop(unk)
    for nt in rules:
        wmap_idx = output_rule(nt, rules, ids, wmap_idx, f, f_w)

from __future__ import division
from collections import deque, Counter
from itertools import izip_longest

PARTIAL_MATCH_CONSTANT = 0.5

class PrefixRanker(object):

    @staticmethod
    def get_atoms(tree):
        pairs = []
        extras = []
        for s1, s2, dh, dv, path in tree.get_pairs():
            pairs.append('|'.join(map(unicode, [s1, s2, dh, dv])))
            extras.append(''.join(map(str, path)))
        return pairs, extras, len(pairs)

    @staticmethod
    def rank(match_pairs, search_extras, search_size, result_size, pair_counts, total_exprs):
        matches = Counter()
        for pair, path in match_pairs:
            search_path = search_extras[pair]
            path_prefix = prefix(search_path, path)
            matches[path_prefix] += 1
        
        _, num_matches = matches.most_common(1)[0]
        num_matches += (len(match_pairs) - num_matches) * PARTIAL_MATCH_CONSTANT
        precision = num_matches / result_size
        recall = num_matches / search_size
        return 2 * (precision * recall) / (precision + recall)

def prefix(search_path, result_path):
    result = deque()
    mismatched = False
    for s, r in izip_longest(reversed(search_path), reversed(result_path)):
        if r == s:
            if mismatched:
                result.appendleft(r)
        else:
            mismatched = True
            if r == '0':
                if s == '1':
                    result.appendleft('a')
                elif s == '2':
                    result.appendleft('b')
                elif s is None:
                    result.appendleft('c')
            elif r == '1':
                if s == '0':
                    result.appendleft('d')
                elif s == '2':
                    result.appendleft('e')
                elif s is None:
                    result.appendleft('f')
            elif r == '2':
                if s == '0':
                    result.appendleft('0')
                elif s == '1':
                    result.appendleft('g')
                elif s is None:
                    result.appendleft('i')
            elif r is None:
                if s == '0':
                    result.appendleft('j')
                elif s == '1':
                    result.appendleft('k')
                elif s == '2':
                    result.appendleft('l')

    return ''.join(result)

from __future__ import division
from collections import deque, Counter
from itertools import izip_longest

PARTIAL_MATCH_CONSTANT = 0.5

class PrefixRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return len(search_pairs)

    result_score_key = 'prefix_score'
    fetch_paths = True

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        matches = Counter()
        for pair, path in match_pairs:
            for search_path in search_paths[pair]:
                path_prefix = prefix(search_path, path)
                matches[path_prefix] += 1
        
        _, num_matches = matches.most_common(1)[0]
        #num_matches += (len(match_pairs) - num_matches) * PARTIAL_MATCH_CONSTANT
        return 2 * num_matches / (search_score + result_score)

def prefix(search_path, result_path):
    i = 0
    try:
        while search_path[i - 1] == result_path[i - 1]:
            i -= 1
    except:
        pass
    if i == 0:
        return search_path, result_path
    else:
        return search_path[:i], result_path[:i]

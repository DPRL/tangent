from __future__ import division
from math import log
from collections import deque, Counter, defaultdict
from itertools import izip_longest, izip

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

def idf(count, total):
    return log(total / (count + 1), 10)

class TfIdfPrefixRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        if pair_counts != None and total_exprs != None:
            return sum(idf(pair_counts[p], total_exprs) for p in search_pairs)
        else:
            return len(search_pairs)

    result_score_key = 'tfidfprefix_score'
    fetch_paths = True

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        matches = defaultdict(float)
        for pair, path in match_pairs:
            pair_score = idf(pair_counts[pair], total_exprs)
            for search_path in search_paths[pair]:
                path_prefix = prefix(search_path, path)
                matches[path_prefix] += pair_score
        
        match_score = max(matches.values())
        return 2 * match_score / (search_score + result_score)

    @staticmethod
    def second_pass(db):
        pipe = db.pipeline()
        all_pairs = list(db.smembers('all_pairs'))
        for p in all_pairs:
            pipe.llen('pair:%s:exprs' % p)
        all_counts = dict((pair, int(count)) for (pair, count) in izip(all_pairs, pipe.execute()))

        num_exprs = int(db.get('next_expr_id')) + 1
        for i in range(num_exprs):
            pairs = db.lrange('expr:%d:all_pairs' % i, 0, -1)
            score = sum(idf(all_counts[p], num_exprs) for p in pairs)
            db.set('expr:%d:tfidfprefix_score' % i, score)

from __future__ import division
from math import log
from itertools import izip

def idf(counts, total):
    return sum(log(total / (c + 1), 10) for c in counts)

class TfIdfRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        if pair_counts != None and total_exprs != None:
            return idf((pair_counts[p] for p in search_pairs), total_exprs)
        else:
            return len(search_pairs)

    result_score_key = 'tfidf_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        match_score = idf((pair_counts[p] for p in match_pairs), total_exprs)
        if 2 * match_score / (search_score + result_score) > 1:
            import ipdb; ipdb.set_trace()
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
            counts = (all_counts[p] for p in pairs)
            db.set('expr:%d:tfidf_score' % i, idf(counts, num_exprs))

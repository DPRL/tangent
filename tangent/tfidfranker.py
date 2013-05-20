from __future__ import division
from math import log

def idf(counts, total):
    return sum(log(total / c, 10) for c in counts)

class TfIdfRanker(object):

    @staticmethod
    def get_atoms(tree):
        pairs = []
        for s1, s2, dh, dv, path in tree.get_pairs():
            pairs.append('|'.join(map(unicode, [s1, s2, dh, dv])))
        return pairs, [], len(pairs)

    @staticmethod
    def rank(match_pairs, search_pairs, search_size, result_size, pair_counts, total_exprs):
        match = idf((pair_counts[p[0]] for p in match_pairs), total_exprs)
        search = idf((pair_counts[p] for p in search_pairs.keys()), total_exprs)
        return 2 * match / (search + result_size)

    @staticmethod
    def second_pass(db):
        num_exprs = int(db.get('next_expr_id'))
        for i in range(num_exprs):
            pairs = db.smembers('expr:%d:all_pairs' % i)
            pipe = db.pipeline()
            for p in pairs:
                pipe.scard('pair:%s:exprs' % p)
            counts = map(int, pipe.execute())
             
            db.set('expr:%d:num_pairs' % i, idf(counts, num_exprs))

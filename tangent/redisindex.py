from __future__ import division
from collections import Counter
from operator import itemgetter

import redis

from tangent import Index

class RedisIndex(Index):
    def __init__(self):
        self.r = redis.StrictRedis()
        
    def add(self, tree):
        # Get a unique id for the expression.
        expr_id = self.r.incr('next_expr_id')

        pairs = set(tree.get_pairs())
        pipe = self.r.pipeline()

        # Insert the source text and number of pairs of the expression.
        pipe.set('expr:%d:text' % expr_id, tree.get_html())
        pipe.set('expr:%d:num_pairs' % expr_id, len(pairs))
        
        # Insert each pair.
        for pair in pairs:
            pipe.sadd('pair:%s:exprs' % str(pair[:-1]), expr_id)

        pipe.execute()

    def search(self, search_tree):
        match_counts = Counter()
        pipe = self.r.pipeline()
        
        # Get expressions that contain each pair and count them.
        for pair in search_tree.get_pairs():
            pipe.smembers('pair:%s:exprs' % str(pair[:-1]))
        for members in pipe.execute():
            match_counts.update([int(x) for x in members])

        # Get number of pairs in each matched expression.
        matches = match_counts.most_common()
        for expr_id, _ in matches:
            pipe.get('expr:%s:num_pairs' % expr_id)
        counts = [int(x) for x in pipe.execute()]

        # Calculate a score for each matched expression.
        final_matches = ((expr_id, f_measure(num_matches, search_tree.num_pairs, result_size))
                         for (expr_id, num_matches), result_size
                         in zip(matches, counts))

        # Get MathML source for expressions to return.
        for expr_id, count in sorted(final_matches, reverse=True, key=itemgetter(1))[:10]:
            yield (self.r.get('expr:%s:text' % expr_id), count)

def f_measure(num_matches, search_size, result_size):
    precision = num_matches / result_size
    recall = num_matches / search_size
    return 2 * (precision * recall) / (precision + recall)

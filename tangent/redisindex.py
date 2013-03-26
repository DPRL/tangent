from __future__ import division
from collections import Counter, defaultdict
from operator import itemgetter

import redis

from tangent import Index

class RedisIndex(Index):
    def __init__(self):
        self.r = redis.StrictRedis()
        
    def add(self, tree):
        # Check if expression is in the index.
        existing_id = self.exact_search(tree)
        if existing_id:
            # Just add the document name to the existing expression.
            self.r.sadd('expr:%s:doc' % existing_id, tree.document)
        else:
            # Get a unique id for the expression.
            expr_id = self.r.incr('next_expr_id')

            pairs = set(tree.get_pairs())
            pipe = self.r.pipeline()

            # Insert the source text and number of pairs of the expression.
            pipe.set('expr:%d:text' % expr_id, tree.get_html())
            pipe.set('expr:%d:num_pairs' % expr_id, len(pairs))
            pipe.sadd('expr:%d:doc' % expr_id, tree.document)
            
            # Insert each pair.
            for pair in pairs:
                pipe.sadd('pair:%s:exprs' % str(pair[:-1]), expr_id)

            pipe.execute()

    def search(self, search_tree):
        match_lists = defaultdict(list)
        pipe = self.r.pipeline()
        pairs = [str(pair[:-1]) for pair in search_tree.get_pairs()]

        # Get expressions that contain each pair and count them.
        for pair in pairs:
            pipe.smembers('pair:%s:exprs' % pair)
        for pair, expressions in zip(pairs, pipe.execute()):
            for e in expressions:
                match_lists[int(e)].append(pair)

        # Get number of pairs in each matched expression.
        matches = match_lists.items()
        for expr_id, _ in matches:
            pipe.get('expr:%d:num_pairs' % expr_id)
        counts = [int(x) for x in pipe.execute()]

        # Calculate a score for each matched expression.
        final_matches = ((expr_id, f_measure(len(match_pairs), search_tree.num_pairs, result_size), match_pairs)
                         for (expr_id, match_pairs), result_size
                         in zip(matches, counts))

        # Get MathML source for expressions to return.
        for expr_id, count, match_pairs in sorted(final_matches, reverse=True, key=itemgetter(1))[:10]:
            yield (self.r.get('expr:%s:text' % expr_id), count, match_pairs, self.r.smembers('expr:%s:doc' % expr_id))

    def exact_search(self, search_tree):
        pairs = ['pair:%s:exprs' % str(pair[:-1]) for pair in search_tree.get_pairs()]

        # Get the expressions that contain all pairs.
        if len(pairs) == 0:
            return None
        elif len(pairs) == 1:
            match_ids = self.r.smembers(pairs[0])
        else:
            match_ids = self.r.sinter(*pairs)
            
        # If no such expressions, return None.
        if len(match_ids) <= 0:
            return None

        # Find an expression that has exactly as many pairs.
        pipe = self.r.pipeline()
        for expr_id in match_ids:
            pipe.get('expr:%s:num_pairs' % expr_id)
        counts = [int(x) for x in pipe.execute()]
        for expr_id, count in zip(match_ids, counts):
            if count == len(pairs):
                return expr_id
        else:
            return None
        

def f_measure(num_matches, search_size, result_size):
    precision = num_matches / result_size
    recall = num_matches / search_size
    return 2 * (precision * recall) / (precision + recall)

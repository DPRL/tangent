from __future__ import division
from collections import Counter, defaultdict
from operator import itemgetter
from itertools import izip_longest

import redis

from tangent import Index, FMeasureRanker

class RedisIndex(Index):
    def __init__(self, ranker=None):
        self.r = redis.StrictRedis()
        if ranker:
            self.ranker = ranker
        else:
            self.ranker = FMeasureRanker()
        
    def add(self, tree):
        # Check if expression is in the index.
        existing_id = self.exact_search(tree)
        if existing_id:
            # Just add the document name to the existing expression.
            self.r.sadd('expr:%s:doc' % existing_id, tree.document)
        else:
            # Get a unique id for the expression.
            expr_id = self.r.incr('next_expr_id')

            pairs, extras = self.ranker.get_atoms(tree)
            pipe = self.r.pipeline()

            # Insert the source text and number of pairs of the expression.
            pipe.set('expr:%d:text' % expr_id, tree.get_html())
            pipe.set('expr:%d:num_pairs' % expr_id, len(pairs))
            pipe.sadd('expr:%d:doc' % expr_id, tree.document)

            # Create an index from tree to its id, so we can do exact search.
            pipe.set(u'tree:%s' % tree.build_repr(), expr_id)
            
            # Insert each pair.
            for pair, extra in izip_longest(pairs, extras):
                if extra:
                    value = '%d:%s' % (expr_id, extra)
                else:
                    value = expr_id
                pipe.sadd('pair:%s:exprs' % pair, value)

            pipe.execute()

    def search(self, search_tree):
        match_lists = defaultdict(list)
        pipe = self.r.pipeline()
        pairs, _ = self.ranker.get_atoms(search_tree)

        # Get expressions that contain each pair and count them.
        for pair in pairs:
            pipe.smembers('pair:%s:exprs' % pair)
        for pair, expressions in zip(pairs, pipe.execute()):
            for e in expressions:
                if ':' in e:
                    exp, extra = e.split(':')
                    match_lists[int(exp)].append((pair, extra))
                else:
                    match_lists[int(e)].append((pair, None))

        # Get number of pairs in each matched expression.
        matches = match_lists.items()
        for expr_id, _ in matches:
            pipe.get('expr:%d:num_pairs' % expr_id)
        counts = [int(x) for x in pipe.execute()]

        # Calculate a score for each matched expression.
        final_matches = ((expr_id, 
                          self.ranker.rank(match_pairs, search_tree.num_pairs, result_size),
                          match_pairs)
                         for (expr_id, match_pairs), result_size
                         in zip(matches, counts))

        # Get MathML source for expressions to return.
        for expr_id, count, match_pairs in sorted(final_matches, reverse=True, key=itemgetter(1))[:10]:
            yield (self.r.get('expr:%s:text' % expr_id), count, match_pairs, self.r.smembers('expr:%s:doc' % expr_id), expr_id)

    def exact_search(self, search_tree):
        return self.r.get(u'tree:%s' % search_tree.build_repr())

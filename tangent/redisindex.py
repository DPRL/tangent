from __future__ import division
from collections import Counter, defaultdict
from operator import itemgetter
from itertools import izip_longest
from random import randint
import re

import redis

from tangent import Index, Result, FMeasureRanker

class RedisIndex(Index):
    def __init__(self, ranker=None, db=0):
        self.r = redis.StrictRedis(db=db)
        if ranker:
            self.ranker = ranker
        else:
            self.ranker = FMeasureRanker()

    def random(self):
        expr_count = int(self.r.get('next_expr_id'))
        expr_id = randint(0, expr_count - 1)
        return self.r.get('expr:%d:text' % expr_id)
        
    def add(self, tree):
        # Check if expression is in the index.
        existing_id = self.exact_search(tree)
        if existing_id:
            # Just add the document name to the existing expression.
            self.r.sadd('expr:%s:doc' % existing_id, tree.document)
        else:
            # Get a unique id for the expression.
            expr_id = self.r.incr('next_expr_id')

            pairs, extras, num_atoms = self.ranker.get_atoms(tree)
            pipe = self.r.pipeline()

            # Insert the source text and number of pairs of the expression.
            pipe.set('expr:%d:text' % expr_id, tree.get_html())
            pipe.set('expr:%d:num_pairs' % expr_id, num_atoms)
            pipe.sadd('expr:%d:doc' % expr_id, tree.document)

            # Create an index from tree to its id, so we can do exact search.
            pipe.set(u'tree:%s' % tree.build_repr(), expr_id)
            
            # Insert each pair in the inverted lists.
            for pair, extra in izip_longest(pairs, extras):
                if extra:
                    value = '%d:%s' % (expr_id, extra)
                else:
                    value = expr_id
                pipe.sadd('pair:%s:exprs' % pair, value)

            # Create set of all pairs.
            for p in pairs:
                self.r.sadd('expr:%d:all_pairs' % expr_id, p)
                self.r.sadd('all_pairs', p)

            pipe.execute()

    def search(self, search_tree):
        match_lists = defaultdict(list)
        pipe = self.r.pipeline()
        pairs, extras, num_atoms= self.ranker.get_atoms(search_tree)
        search_extras = dict(izip_longest(pairs, extras))
        pair_counts = dict()
        total_exprs = int(self.r.get('next_expr_id'))

        # Get expressions that contain each pair and count them.
        for pair in pairs:
            pipe.smembers('pair:%s:exprs' % pair)
        for pair, expressions in zip(pairs, pipe.execute()):
            pair_counts[pair] = len(expressions)
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
        counts = [float(x) for x in pipe.execute()]

        # Calculate a score for each matched expression.
        final_matches = ((expr_id, 
                          self.ranker.rank(match_pairs, search_extras, num_atoms, result_size, pair_counts, total_exprs),
                          match_pairs)
                         for (expr_id, match_pairs), result_size
                         in zip(matches, counts))

        # Get MathML source for expressions to return.
        results = []
        for expr_id, count, match_pairs in sorted(final_matches, reverse=True, key=itemgetter(1))[:10]:
            results.append(Result(mathml=self.r.get('expr:%s:text' % expr_id),
                                  score=count,
                                  debug_info=['Pairs: %s' % match_pairs],
                                  links=self.get_document_links(expr_id),
                                  expr_id=expr_id))
        return results, len(matches), pair_counts

    def second_pass(self):
        try:
            self.ranker.second_pass(self.r)
        except AttributeError:
            # Ranker does not have a second pass method, so do nothing.
            pass

    def exact_search(self, search_tree):
        return self.r.get(u'tree:%s' % search_tree.build_repr())

    def get_document_links(self, expr_id):
        docs = self.r.smembers('expr:%s:doc' % expr_id)
        return [self.create_document_link(d) for d in docs]

    def create_document_link(self, path):
        match = re.search(r'(/\d\d\d\d/.*)', path)
        if match:
            return 'http://saskatoon.cs.rit.edu/mrec' +  match.group()
        else:
            return path

"""
    Tangent
    Copyright (c) 2013 David Stalnaker, Richard Zanibbi

    This file is part of Tangent.

    Tanget is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Tangent is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tangent.  If not, see <http://www.gnu.org/licenses/>.

    Contact:
        - David Stalnaker: david.stalnaker@gmail.com
        - Richard Zanibbi: rlaz@cs.rit.edu
"""
from __future__ import division
from collections import Counter, defaultdict
from operator import itemgetter
from itertools import izip_longest
from random import randint
import urllib
import re

import redis

from tangent import Index, Result, FMeasureRanker, DistanceRanker, RecallRanker, PrefixRanker, TfIdfRanker, EverythingRanker, TfIdfPrefixRanker

class RedisIndex(Index):
    def __init__(self, ranker=None, db=0):
        self.r = redis.StrictRedis(db=db)
        if ranker:
            self.ranker = ranker
        else:
            self.ranker = FMeasureRanker()
        self.all_rankers = [FMeasureRanker(), DistanceRanker(), RecallRanker(), PrefixRanker(), TfIdfRanker(), EverythingRanker(), TfIdfPrefixRanker()]

    def random(self):
        """
        Return the tex of a random expression

        :rtype: string
        :return: the latex of a random expression

        """
        expr_count = int(self.r.get('next_expr_id'))
        expr_id = randint(0, expr_count - 1)
        return self.r.get('expr:%d:latex' % expr_id)
        
    def add(self, tree):
        """
        Add symbol tree to index

        :type tree: SymbolTree
        :param tree:Symbol Tree


        """
        # Check if expression is in the index.
        existing_id = self.exact_search(tree)
        if existing_id:
            # Just add the document name to the existing expression.
            self.r.sadd('expr:%s:doc' % existing_id, tree.document)
        else:
            # Get a unique id for the expression.
            expr_id = self.r.incr('next_expr_id')

            pairs = tree.get_pairs(get_paths=True)
            pipe = self.r.pipeline()

            # Insert the source text and number of pairs of the expression.
            pipe.set('expr:%d:mathml' % expr_id, tree.mathml)
            pipe.set('expr:%d:latex' % expr_id, tree.latex)
            pipe.sadd('expr:%d:doc' % expr_id, tree.document)

            # Add the max result score for each ranker.
            for ranker in self.all_rankers:
                score = ranker.search_score(pairs[0])
                pipe.set('expr:%d:%s' % (expr_id, ranker.result_score_key),
                         score)

            # Create an index from tree to its id, so we can do exact search.
            pipe.set(u'tree:%s' % tree.build_repr(), expr_id)
            
            # Insert each pair in the inverted lists.
            for pair, path in zip(*pairs):
                pipe.lpush('pair:%s:exprs' % pair, expr_id)
                pipe.lpush('pair:%s:paths' % pair, path)

            # Create set of all pairs.
            for pair, path in zip(*pairs):
                pipe.rpush('expr:%d:all_pairs' % expr_id, pair)
                pipe.rpush('expr:%d:all_paths' % expr_id, path)
                pipe.sadd('all_pairs', pair)

            pipe.execute()

    def search(self, search_tree):
        """
        Return all matches for this search tree

        :type search_tree: SymbolTree
        :param search_tree:Symbol Tree


        :rtype: list[Result]
        :return: list of search results

        """
        
        matches = defaultdict(list)
        pair_counts = dict()
        total_exprs = int(self.r.get('next_expr_id')) + 1
        pipe = self.r.pipeline()

        search_pairs, paths = search_tree.get_pairs(get_paths=True)
        search_paths = defaultdict(list)
        for pair, path in zip(search_pairs, paths):
            search_paths[pair].append(path)
        search_pair_counts = Counter(search_pairs).items()
        
        # Get expressions that contain each pair and count them.
        if self.ranker.fetch_paths:
            pipe2 = self.r.pipeline()
            for pair, count in search_pair_counts:
                pipe.lrange('pair:%s:exprs' % pair, 0, -1)
                pipe2.lrange('pair:%s:paths' % pair, 0, -1)
            for (pair, count), expressions, paths in zip(search_pair_counts,
                                                         pipe.execute(),
                                                         pipe2.execute()):
                pair_counts[pair] = len(expressions)
                for e, path in zip(expressions, paths):
                    matches[int(e)].append((pair, path))
        else:
            for pair, count in search_pair_counts:
                pipe.lrange('pair:%s:exprs' % pair, 0, -1)
            for (pair, count), expressions in zip(search_pair_counts,
                                                  pipe.execute()):
                pair_counts[pair] = len(expressions)
                prev = None
                for e in expressions:
                    match_count = match_count + 1 if e == prev else 1
                    if match_count <= count:
                        matches[int(e)].append(pair)
                    prev = e


        # Get number of pairs in each matched expression.
        for expr_id in matches.keys():
            pipe.get('expr:%d:%s' % (expr_id, self.ranker.result_score_key))
        result_scores = [float(x) for x in pipe.execute()]

        # Get max score for the search term
        search_score = self.ranker.search_score(search_pairs, pair_counts,
                                                total_exprs)

        # Calculate a score for each matched expression.
        ranked_matches = ((expr_id, 
                           self.ranker.rank(match_pairs, search_score,
                                            result_score, pair_counts,
                                            total_exprs, search_paths),
                           match_pairs)
                          for (expr_id, match_pairs), result_score
                          in zip(matches.items(), result_scores))
        
        # Sort the results, and get additional information for the top results.
        results = []
        for expr_id, count, match_pairs in sorted(ranked_matches, reverse=True,
                                                  key=itemgetter(1))[:10]:
            results.append(Result(latex=self.r.get('expr:%s:latex' % expr_id),
                                  score=count,
                                  debug_info=['Pairs: %s' % match_pairs],
                                  links=self.get_document_links(expr_id),
                                  expr_id=expr_id))
        return results, len(matches), pair_counts

    def second_pass(self):
        """
        Apply any post calculation required by rankers
        """
        for ranker in self.all_rankers:
            try:
                ranker.second_pass(self.r)
            except AttributeError:
                # Ranker does not have a second pass method, so do nothing.
                pass

    def exact_search(self, search_tree):
        """
        Return symbols in symbol tree in index if any

        :type search_tree:str
        :param search_tree: symbol pair

        :rtype: string
        :return: symbol path of tree

        """
        return self.r.get(u'tree:%s' % search_tree.build_repr())

    def get_document_links(self, expr_id):
        """
        Return all links that expression occurs in

        :type expr_id:int
        :param expr_id:expression id


        :rtype: list[(str,str)]
        :return: list of of  wikipedia link
        """
        docs = self.r.smembers('expr:%s:doc' % expr_id)
        return [self.create_document_link(d) for d in docs]

    def create_document_link(self, path):
        """
        Given the path of the document, return the direct wikipedia link and the name of the article

        :type path:str
        :param path:wikipedia link

        :rtype: (str,str)
        :return: wikipedia link and title of article
        """
        match = re.search(r'([^/]*)\.mml', path)
        if match:
            return 'http://en.wikipedia.org/w/index.php?search=%s&go=Go' % urllib.quote(match.group(1)), 'Wikipedia - ' + match.group(1)
        else:
            return path, path

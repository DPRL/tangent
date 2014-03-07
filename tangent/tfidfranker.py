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
from math import log
from itertools import izip

def idf(counts, total):
    return sum(log(total / (c + 1), 10) for c in counts)

class TfIdfRanker(object):
    """
    The TFIDFRanker ranker adapts the common text search metric of TF-IDF
    (term frequency - inverse document frequency) to the math domain. The
    formula ends up being quite different tan that of text search, but the basic
    idea is the same: apply more weight to uncommon pairs (terms). We use
    the same f-measure metric, but instead of counting the number of pairs that
    match, we sum the inverse expression frequency (IEF) of each matched pair.


    score =\frac {2 \sum_{p\varepsilon \epsilon M} ief(p)}
         {{\sum_{p\varepsilon \epsilon Q}ief(p)} +{\sum_{p\varepsilon \epsilon R}ief(p)}}

         where ief=inverse expression frequency
    """
    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        """
        Score for search pairs is idf or the length of search pairs

        :type search_pairs: list
        :param search_pairs: list of symbol pairs

        :rtype: double
        :return: score for this expression

        """
        if pair_counts != None and total_exprs != None:
            return idf((pair_counts[p] for p in search_pairs), total_exprs)
        else:
            return len(search_pairs)

    result_score_key = 'tfidf_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        """
        Returns tf-idf based score

        :type match_pairs: list
        :param match_pairs list of pairs that latched

        :type search_score: double
        :param search_score: score for pairs in query

        :type result_score: double
        :param result_score: score for pairs that matched


        :type pair_counts: dict(str,int)
        :param pair_counts: frequency for each symbol pair

        :type total_exprs:
        :param total_exprs:

        :type search_paths:dict(str,list)
        :param: search_paths:given two symbol pairs, the path between them

        :rtype: double
        :return: score

        """

        match_score = idf((pair_counts[p] for p in match_pairs), total_exprs)
        return 2 * match_score / (search_score + result_score)

    @staticmethod
    def second_pass(db):
        """
        Update the idf score of the expressions

        :type db: StrictRedis
        :param db: Redis Database connection object

        """
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

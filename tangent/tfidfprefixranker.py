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
from collections import deque, Counter, defaultdict
from itertools import izip_longest, izip

def prefix(search_path, result_path):
    """
    Return shared prefix
    """
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
    """
    Return idf
    """
    return log(total / (count + 1), 10)

class TfIdfPrefixRanker(object):
    """
    The TfIdfPrefixRanker looks at a way to find an alignment
    between the query and result expressions and only include pairs in the match if
    they occur on that alignment.


    score = 2|prefix(M) | /  ( |Q| + |R|)

    """

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        """
        Score for search pairs is the sum of the idf or the length of search pairs

        :type search_pairs: list
        :param search_pairs: list of symbol pairs

        :rtype: double
        :return: score for this expression

        """

        if pair_counts != None and total_exprs != None:
            return sum(idf(pair_counts[p], total_exprs) for p in search_pairs)
        else:
            return len(search_pairs)

    result_score_key = 'tfidfprefix_score'
    fetch_paths = True

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        """
        Returns tf-idf-prefix based score

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
        """
        Update the prefix score of the expressions

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
            score = sum(idf(all_counts[p], num_exprs) for p in pairs)
            db.set('expr:%d:tfidfprefix_score' % i, score)

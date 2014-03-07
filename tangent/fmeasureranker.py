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


class FMeasureRanker(object):
    """
    FMeasureRanker calculate the fscore between two expressions's symbol tree

    Precision = percentage of matched symbols
    Recall = percentage of symbol pairs in the query that are in match

    FMeasure = 2|M| /  ( |Q| + |R|)

    Q= set of pairs in the query
    R= set of pairs in the result candidate
   |M| = set of pairs that matched
    """

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        """
        Maximum score for search pairs is the number of symbol pairs

        :type search_pairs: list
        :param search_pairs: list of symbol pairs

        :rtype: int
        :return: number of symbol pairs

        """
        return len(search_pairs)

    result_score_key = 'fmeasure_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        """
        Returns f-score

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
        :return: fscore

        """
        num_matches = len(match_pairs)
        return 2 * num_matches / (search_score + result_score)

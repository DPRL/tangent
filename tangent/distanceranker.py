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
class DistanceRanker(object):
    """
   The Distance ranker gives higher weights to the pairs whose symbols are closer. Each pair is weighted by 1/dh, which has the effect of giving more importance to the pairs that are closer together. The ranker modifies the F-Measure thusly: instead of counting the set of pairs in each of M, Q, and R, we sum this 1/dh weight for each Symbol Pair in the set.
   
   \frac {2 \sum_{p\varepsilon \epsilon M} \frac{1}{p.d{h}}}
         {{\sum_{p\varepsilon \epsilon Q}\frac{1}{p.d{h}}} +{\sum_{p\varepsilon \epsilon R}\frac{1}{p.d{h}}}}
   
   where p.d{h} is the d_{h} value for p
   
   """

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        """
        Maximum score for search pairs is the sum of 1/horizontal distance

        :type search_pairs: list
        :param search_pairs: list of symbol pairs

        :rtype: double
        :return: max score for this expression

        """
        return sum(1 / int(pair.split('|')[2]) for pair in search_pairs)

    result_score_key = 'distance_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        """
        Returns distance based score

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
        :return: distance score

        """
        match_score = sum(1 / int(pair.split('|')[2]) for pair in match_pairs)
        return 2 * match_score / (search_score + result_score)

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
class RecallRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return len(search_pairs)

    result_score_key = 'recall_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        num_matches = len(match_pairs)
        return 3.25 * num_matches / (2.25 * search_score + result_score)

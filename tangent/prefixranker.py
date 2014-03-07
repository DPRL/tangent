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
from collections import deque, Counter
from itertools import izip_longest

PARTIAL_MATCH_CONSTANT = 0.5

class PrefixRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return len(search_pairs)

    result_score_key = 'prefix_score'
    fetch_paths = True

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        matches = Counter()
        for pair, path in match_pairs:
            for search_path in search_paths[pair]:
                path_prefix = prefix(search_path, path)
                matches[path_prefix] += 1
        
        _, num_matches = matches.most_common(1)[0]
        #num_matches += (len(match_pairs) - num_matches) * PARTIAL_MATCH_CONSTANT
        return 2 * num_matches / (search_score + result_score)

def prefix(search_path, result_path):
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

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

from symboltree import SymbolTree
from fmeasureranker import FMeasureRanker
from distanceranker import DistanceRanker
from prefixranker import PrefixRanker
from recallranker import RecallRanker
from tfidfranker import TfIdfRanker
from everythingranker import EverythingRanker
from tfidfprefixranker import TfIdfPrefixRanker
from index import Index, Result
from redisindex import RedisIndex

__all__ = ['SymbolTree', 'Index', 'Result', 'RedisIndex', 'FMeasureRanker', 'DistanceRanker', 'RecallRanker', 'PrefixRanker', 'PrefixRanker', 'TfIdfPrefixRanker']

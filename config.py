"""
    DPRL Math Symbol Recognizers
    Copyright (c) 2012-2014 David Stalnaker, Richard Zanibbi

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

from tangent import FMeasureRanker, DistanceRanker, RecallRanker, PrefixRanker, TfIdfRanker, EverythingRanker, TfIdfPrefixRanker

class Config(object):
    DEBUG = True
    TESTING = True
    HOST = '0.0.0.0'

class FMeasureConfig(Config):
    RANKER = FMeasureRanker()
    DATABASE = 0
    PORT = 9002

class DistanceConfig(Config):
    RANKER = DistanceRanker()
    DATABASE = 0
    PORT = 9003

class RecallConfig(Config):
    RANKER = RecallRanker()
    DATABASE = 0
    PORT = 9004

class PrefixConfig(Config):
    RANKER = PrefixRanker()
    DATABASE = 0
    PORT = 9005

class TfIdfConfig(Config):
    RANKER = TfIdfRanker()
    DATABASE = 0
    PORT = 9006

class EverythingConfig(Config):
    RANKER = EverythingRanker()
    DATABASE = 0
    PORT = 9007

class TfIdfPrefixConfig(Config):
    RANKER = TfIdfPrefixRanker()
    DATABASE = 0
    PORT = 9008

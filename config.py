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

"""
Different Types of Config that specify different ranking algorithms

"""

from tangent import FMeasureRanker, DistanceRanker, RecallRanker, PrefixRanker, TfIdfRanker, EverythingRanker, \
    TfIdfPrefixRanker


class Config(object):
    """
    Uses the default ranker: FMeasureConfig and default database
    """
    DEBUG = True
    TESTING = True
    HOST = '0.0.0.0'


class FMeasureConfig(Config):
    """
    Uses the FMeasureRanker and default database
    """
    RANKER = FMeasureRanker()
    DATABASE = 0
    PORT = 9002


class DistanceConfig(Config):
    """
    Uses the DistanceRanker and default database
    """
    RANKER = DistanceRanker()
    DATABASE = 0
    PORT = 9003


class RecallConfig(Config):
    """
    Uses the RecallRanker and default database
    """
    RANKER = RecallRanker()
    DATABASE = 0
    PORT = 9004


class PrefixConfig(Config):
    """
    Uses the PrefixRanker and default database
    """
    RANKER = PrefixRanker()
    DATABASE = 0
    PORT = 9005


class TfIdfConfig(Config):
    """
    Uses the TFIdfRanker and default database
    """
    RANKER = TfIdfRanker()
    DATABASE = 0
    PORT = 9006


class EverythingConfig(Config):
    """
    Uses the Everything Ranker and default database
    """
    RANKER = EverythingRanker()
    DATABASE = 0
    PORT = 9007


class TfIdfPrefixConfig(Config):
    """
    Uses the TfIdfRanker and default database
    """
    RANKER = TfIdfPrefixRanker()
    DATABASE = 0
    PORT = 9008

from tangent import FMeasureRanker, DistanceRanker, RecallRanker

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
    DATABASE = 1
    PORT = 9003

class RecallConfig(Config):
    RANKER = RecallRanker()
    DATABASE = 1
    PORT = 9004

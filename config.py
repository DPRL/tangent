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

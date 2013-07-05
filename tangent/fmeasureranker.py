from __future__ import division
class FMeasureRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return len(search_pairs)

    result_score_key = 'fmeasure_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        num_matches = len(match_pairs)
        return 2 * num_matches / (search_score + result_score)

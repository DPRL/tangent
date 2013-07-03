from __future__ import division
class RecallRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return len(search_pairs)

    result_score_key = 'recall_score'

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs):
        num_matches = len(match_pairs)
        return 3.25 * num_matches / (2.25 * search_score + result_score)

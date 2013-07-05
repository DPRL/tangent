from __future__ import division
class DistanceRanker(object):

    @staticmethod
    def search_score(search_pairs, pair_counts=None, total_exprs=None):
        return sum(1 / int(pair.split('|')[2]) for pair in search_pairs)

    result_score_key = 'distance_score'
    fetch_paths = False

    @staticmethod
    def rank(match_pairs, search_score, result_score, pair_counts, total_exprs, search_paths):
        match_score = sum(1 / int(pair.split('|')[2]) for pair in match_pairs)
        return 2 * match_score / (search_score + result_score)

from __future__ import division
class FMeasureRanker(object):

    @staticmethod
    def get_atoms(tree):
        pairs = []
        extras = []
        for s1, s2, dh, dv, path in tree.get_pairs():
            pairs.append('|'.join(map(unicode, [s1, s2, dh, dv])))
            extras.append(''.join(map(str, path)))
        return pairs, extras

    @staticmethod
    def rank(matches, search_size, result_size):
        num_matches = len(matches)
        if num_matches == 0:
            return 0.0
        precision = num_matches / result_size
        recall = num_matches / search_size
        return 2 * (precision * recall) / (precision + recall)

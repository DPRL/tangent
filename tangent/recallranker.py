from __future__ import division
class RecallRanker(object):

    @staticmethod
    def get_atoms(tree):
        pairs = []
        extras = []
        count = 0.0
        for s1, s2, dh, dv, path in tree.get_pairs():
            pairs.append('|'.join(map(unicode, [s1, s2, dh, dv])))
            extras.append(''.join(map(str, path)))
            count += 1 / dh
        return pairs, extras, count


    @staticmethod
    def rank(match_pairs, search_pairs, search_size, result_size):
        count = 0.0
        for match in match_pairs:
            _, _, dh, _ = match[0].split('|')
            count += 1/ float(dh)
        if count == 0.0:
            return 0.0
        precision = count / result_size
        recall = count / search_size
        return 3.25 * (precision * recall) / (2.25 * precision + recall)

class FMeasureRanker(object):

    @staticmethod
    def get_atoms(tree):
        for s1, s2, dh, dv, _ in tree.get_pairs():
            yield str((s1, s2, dh, dv))

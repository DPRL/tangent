from __future__ import division

from tangent import Index, PairIndex, SymbolIndex

class CombinationIndex(Index):
    def __init__(self):
        self.indices = [PairIndex(), SymbolIndex()]
    
    def get_size(self):
        return sum(map(lambda x: x.get_size(), self.indices)) / len(self.indices)

    def add(self, tree):
        for index in self.indices:
            index.add(tree)

    def search(self, search_tree):
        results = dict()
        for index in self.indices:
            for tree, score in index.search(search_tree):
                if tree in results:
                    results[tree] += score
                else:
                    results[tree] = score
        return results.items()

from __future__ import division

from collections import Counter, defaultdict

from tangent import Index

class SymbolIndex(Index):
    def __init__(self):
        self.index = defaultdict(Counter)
        self.size = 0

    def get_size(self):
        return self.size

    def add(self, tree):
        self.size += 1
        symbols = map(lambda s: s[0].tag, tree.get_symbols())
        for symbol, count in Counter(symbols).most_common():
            self.index[symbol].update({tree: count})

    def search(self, search_tree):
        results = Counter()
        symbols = map(lambda s: s[0].tag, search_tree.get_symbols())
        for symbol in set(symbols):
            results.update(self.index[symbol])
        for tree, count in results.most_common():
            recall = count / len(symbols)
            precision = count / len(list(tree.get_symbols()))
            f_measure = 2 * (precision * recall) / (precision + recall)
            yield tree, f_measure

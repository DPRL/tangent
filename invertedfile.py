from symboltree import SymbolTree
from collections import Counter, defaultdict

class TreeIndex:
    def __init__(self):
        self.index = defaultdict(Counter)
        self.trees = []

    def add_tex(self, tex):
        self.add(SymbolTree.parse_from_tex(tex))

    def add(self, tree):
        self.trees.append(tree)
        i = len(self.trees) - 1
        for pair in tree.get_pairs():
            self.index[pair][i] += 1

    def search_tex(self, tex):
        return self.search(SymbolTree.parse_from_tex(tex))

    def search(self, search_tree):
        results = Counter()
        pairs = list(search_tree.get_pairs());
        for pair, count in Counter(pairs).items():
            matches = dict(map(lambda x: (x[0], min(x[1], count)), self.index[pair].items()))
            results.update(matches)
        for i, count in results.most_common():
            tree = self.trees[i]
            recall = float(count) / len(pairs)
            precision = float(count) / tree.num_pairs
            f_measure = 2 * (precision * recall) / (precision + recall)
            yield tree, f_measure

class SymbolIndex:
    def __init__(self):
        self.index = defaultdict(Counter)

    def add_tex(self, tex):
        self.add(SymbolTree.parse_from_tex(tex))

    def add(self, tree):
        for symbol, count in Counter(tree.get_symbols()).most_common():
            self.index[symbol].update({tree: count})

    def search_tex(self, tex):
        return self.search(SymbolTree.parse_from_tex(tex))

    def search(self, search_tree):
        results = Counter()
        symbols = search_tree.get_symbols()
        for symbol in set(symbols):
            results.update(self.index[symbol])
        for tree, count in results.most_common():
            recall = float(count) / len(symbols)
            precision = float(count) / len(tree.get_symbols())
            f_measure = 2 * (precision * recall) / (precision + recall)
            yield tree, f_measure

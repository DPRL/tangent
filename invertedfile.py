from symboltree import SymbolTree
from collections import Counter, defaultdict
import os

class Index:
    def add_tex(self, tex):
        self.add(SymbolTree.parse_from_tex(tex))

    def search_tex(self, tex):
        return self.search(SymbolTree.parse_from_tex(tex))

    def add_directory(self, directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                with open(os.path.join(root, filename)) as f:
                    self.add_tex(f.read())

class PairIndex(Index):
    def __init__(self):
        self.index = defaultdict(Counter)
        self.trees = []

    def get_size(self):
        return len(self.trees)

    def add(self, tree):
        self.trees.append(tree)
        i = len(self.trees) - 1
        for pair in tree.get_pairs():
            self.index[pair][i] += 1

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

class SymbolIndex(Index):
    def __init__(self):
        self.index = defaultdict(Counter)

    def get_size(self):
        return len(self.index)

    def add(self, tree):
        for symbol, count in Counter(tree.get_symbols()).most_common():
            self.index[symbol].update({tree: count})

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

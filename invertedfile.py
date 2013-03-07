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
        self.index = defaultdict(list)
        self.trees = []

    def get_size(self):
        return len(self.trees)

    def get_tex(self, i):
        return self.trees[i].get_tex()

    def add(self, tree):
        self.trees.append(tree)
        i = len(self.trees) - 1
        for pair, count in Counter(tree.get_pairs()).items():
            self.index[pair].append((i, count))

    def search(self, search_tree):
        match_counts = Counter()
        pairs = list(search_tree.get_pairs());
        for pair, count in Counter(pairs).items():
            matches = dict(((i, min(count, index_count)) for i, index_count in self.index[pair]))
            match_counts.update(matches)
        results = []
        for i, count in match_counts.most_common():
            tree = self.trees[i]
            recall = float(count) / len(pairs)
            precision = float(count) / tree.num_pairs
            f_measure = 2 * (precision * recall) / (precision + recall)
            results.append((tree.get_tex(), f_measure))
        results.sort(reverse=True, key=lambda x: x[1])
        return results

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
            recall = float(count) / len(symbols)
            precision = float(count) / len(list(tree.get_symbols()))
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

def largest_cc(edges):
    ccs = {}
    for _, _, h_dist, _, right in edges:
        left = right[:-h_dist]
        if left in ccs:
            left_set = ccs[left]
            if right in ccs:
                right_set = ccs[right]
                left_set.merge(right_set)
                for v in right_set:
                    ccs[v] = left_set
            else:
                left_set.add(right)
                ccs[right] = left_set
        else:
            if right in ccs:
                right_set = ccs[right]
                right_set.add(left)
                ccs[left] = right_set
            else:
                cc = ConnectedComponent([left, right])
                ccs[left] = cc
                ccs[right] = cc
    return max(map(lambda x: x.size, ccs.values()))

class ConnectedComponent(set):
    def __init__(self, *args, **kwargs):
        self.size = 1
        super(ConnectedComponent, self).__init__(*args, **kwargs)

    def add(self, elem):
        self.size += 1
        super(ConnectedComponent, self).add(elem)

    def merge(self, elems):
        if self is elems:
            self.size += 1
        else:
            self.size += elems.size - 1
            super(ConnectedComponent, self).update(elems)

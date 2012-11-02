from collections import Counter, defaultdict
from sys import argv
import re
import os
import subprocess

class Symbol:
    def __init__(self, tag, above=None, below=None):
        self.tag = tag
        self.above = above
        self.below = below

class SymbolTree:
    def __init__(self, symbols, filename=None, tex=None):
        self.symbols = symbols if symbols else []
        self.num_pairs = len(list(self.get_pairs()))
        self.filename = filename
        self.tex = tex

    def get_pairs(self):
        for i in range(len(self.symbols)):
            si = self.symbols[i]
            for j in range(i + 1, len(self.symbols)):
                sj = self.symbols[j]
                yield (si.tag, sj.tag, 0, j - i)
            if si.above:
                for j in range(len(si.above.symbols)):
                    sj = si.above.symbols[j]
                    yield (si.tag, sj.tag, 1, j + 1)
                for p in si.above.get_pairs():
                    yield p
            if si.below:
                for j in range(len(si.below.symbols)):
                    sj = si.below.symbols[j]
                    yield (si.tag, sj.tag, -1, j + 1)
                for p in si.below.get_pairs():
                    yield p

    @classmethod
    def parse_from_tex(cls, tex):
        p = subprocess.Popen('txl -q -indent 2 /dev/stdin scripts/FormatModTeX.Txl', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=open('/dev/null', 'r'))
        (output, _) = p.communicate(input=tex)
        t = cls.parse(output.splitlines().__iter__())
        t.tex = tex
        return t

    @classmethod
    def parse(cls, iterator, level=0):
        symbols = []
        while True:
            try:
                l = iterator.next()
            except StopIteration:
                return cls(symbols)
            groups = re.match(r'(?P<whitespace>\s*)(?P<sub>::)?( (?P<type>\S+) (?P<arg>\S+))?', l).groupdict()
            if not groups['sub']:
                symbols.append(Symbol(l.strip()))
            else:
                if not groups['type']:
                    if len(groups['whitespace']) < level:
                        return cls(symbols)
                if groups['type'] == 'REL':
                    iterator.next()
                    if groups['arg'] == '^':
                        symbols[-1].above = cls.parse(iterator, level=level+2)
                    elif groups['arg'] == '_':
                        symbols[-1].below = cls.parse(iterator, level=level+2)


class TreeIndex:
    def __init__(self):
        self.index = defaultdict(Counter)
        self.trees = []

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
        for tree, count in results.most_common():
            recall = float(count) / len(pairs)
            precision = float(count) / self.trees[tree].num_pairs
            f_measure = 2 * (precision * recall) / (precision + recall)
            yield tree, f_measure

if __name__ == '__main__':

    print(list(SymbolTree.parse_from_tex('x^2+y^2').get_pairs()))

    #index = TreeIndex()

    #for root, dirs, files in os.walk(argv[1]):
        #for filename in files:
            #with open(os.path.join(root, filename)) as f:
                #index.add(SymbolTree.parse(f))

    #print(len(index.trees));

    #index.add(SymbolTree([
        #Symbol('x', SymbolTree([
            #Symbol('2'),
            #Symbol('*'),
            #Symbol('z')
        #])),
        #Symbol('+'),
        #Symbol('y', below=SymbolTree([
            #Symbol('z')
        #]))
    #]))

    #index.add(SymbolTree([
        #Symbol('x', SymbolTree([
            #Symbol('2')
        #])),
        #Symbol('+'),
        #Symbol('y')
    #]))

    #index.add(SymbolTree([
        #Symbol('x'),
        #Symbol('+'),
        #Symbol('x'),
        #Symbol('+'),
        #Symbol('x')
    #]))

    #index.add(SymbolTree([
        #Symbol('x'),
        #Symbol('+'),
        #Symbol('x')
    #]))


    #s = SymbolTree([
        #Symbol('x', SymbolTree([
            #Symbol('2'),
            #Symbol('*'),
            #Symbol('b')
        #])),
        #Symbol('+'),
        #Symbol('y', below=SymbolTree([
            #Symbol('z')
        #]))
    #])

    #t = SymbolTree([
        #Symbol('M'),
        #Symbol('='),
        #Symbol('1')
    #])

    ##import pdb; pdb.set_trace()

    #results = sorted(index.search(t), reverse=True, key=lambda x: x[1])

    #for i, score in results:
        #print (index.trees[i].filename, score)

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

    def get_symbols(self):
        symbols = map(lambda x: x.tag, self.symbols)
        for s in self.symbols:
            if s.above:
                symbols.extend(s.above.get_symbols())
            if s.below:
                symbols.extend(s.below.get_symbols())
        return symbols

    def get_tex(self):
        return '${0}$'.format(self.tex)

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

    def __repr__(self):
        return 'SymbolTree({0})'.format(self.tex)

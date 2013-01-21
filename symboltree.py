import re
import os
import subprocess
from collections import deque

class Symbol:
    def __init__(self, tag, next=None, above=None, below=None):
        self.tag = tag
        self.next = next
        self.above = above
        self.below = below
        self.id = None

    def get_symbols(self):
        return SymbolIterator(self)

    def generate_ids(self, prefix=(0,)):
        self.id = prefix
        for child, v_dist in [(self.above, 1), (self.next, 0), (self.below, -1)]:
            if child:
                child.generate_ids(prefix + (v_dist,))

    def get_pairs(self):
        def mk_helper(v_dist_diff):
            def helper(tup):
                right, h_dist, v_dist = tup
                return (self.tag, right.tag, h_dist + 1, v_dist + v_dist_diff, right.id)
            return helper

        ret = []
        for child, v_dist in [(self.above, 1), (self.next, 0), (self.below, -1)]:
            if child:
                ret.extend(map(mk_helper(v_dist), child.get_symbols()))
                ret.extend(child.get_pairs())
        return ret

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

class SymbolIterator(object):
    def __init__(self, node):
        self.stack = deque([(node, 0, 0)] if node else [])

    def __iter__(self):
        return self

    def next(self):
        if len(self.stack) < 1:
            raise StopIteration
        (elem, h_dist, v_dist) = self.stack.pop()
        if elem.below:
            self.stack.append((elem.below, h_dist + 1, v_dist - 1))
        if elem.next:
            self.stack.append((elem.next, h_dist + 1, v_dist))
        if elem.above:
            self.stack.append((elem.above, h_dist + 1, v_dist + 1))
        return (elem, h_dist, v_dist)


class SymbolTree:
    def __init__(self, symbols, filename=None, tex=None):
        self.symbols = symbols
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

def main():
    s = Symbol('x', Symbol('+', Symbol('y', Symbol('*'), Symbol('z'))))
    s.generate_ids()
    print(largest_cc(s.get_pairs()))

if __name__ == '__main__':
    main()

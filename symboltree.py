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

    @classmethod
    def parse(cls, lines):
        #import ipdb; ipdb.set_trace()
        s = cls(lines.popleft().strip())
        ended = False
        while not ended:
            if not lines:
                ended = True
            else:
                next_line = lines[0].strip()
                if next_line == '::':
                    lines.popleft()
                    ended = True
                elif next_line == ':: REL ^':
                    if s.above: 
                        raise Exception
                    lines.popleft()
                    lines.popleft()
                    s.above = cls.parse(lines)
                elif next_line == ':: REL _':
                    if s.below: 
                        raise Exception
                    lines.popleft()
                    lines.popleft()
                    s.below = cls.parse(lines)
                else:
                    if s.next: 
                        raise Exception
                    s.next = cls.parse(lines)
                    ended = True
        return s

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
    def __init__(self, root, tex=None):
        self.root = root
        self.num_pairs = len(list(self.get_pairs()))
        self.tex = tex

    def get_pairs(self):
        return self.root.get_pairs()

    def get_symbols(self):
        return self.root.get_symbols()

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
    def parse(cls, iterator):
        root = Symbol.parse(deque(iterator))
        root.generate_ids()
        return cls(root)

    def __repr__(self):
        return 'SymbolTree({0})'.format(self.tex)


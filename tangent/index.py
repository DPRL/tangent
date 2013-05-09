from __future__ import division
from collections import namedtuple

from tangent import SymbolTree

class Index:
    def search_tex(self, tex):
        return self.search(SymbolTree.parse_from_tex(tex))

    def add_all(self, trees):
        l = len(trees)
        for i, t in enumerate(trees):
            if i % 1000 == 0:
                print('%d / %d' % (i, l))
            self.add(t)

    def add_directory(self, directory):
        self.add_all(SymbolTree.parse_directory(directory)[0])

Result = namedtuple('Result', ['mathml', 'score', 'debug_info', 'links', 'expr_id'])

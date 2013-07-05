from __future__ import division
from collections import namedtuple

from tangent import SymbolTree

class Index:
    def search_tex(self, tex):
        return self.search(SymbolTree.parse_from_tex(tex))

    def add_all(self, trees):
        for t in trees:
            self.add(t)

    def add_directory(self, directory):
        self.add_all(SymbolTree.parse_directory(directory)[0])

    def second_pass():
        pass

Result = namedtuple('Result', ['latex', 'score', 'debug_info', 'links', 'expr_id'])

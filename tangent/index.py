"""
    Tangent
    Copyright (c) 2013 David Stalnaker, Richard Zanibbi

    This file is part of Tangent.

    Tanget is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Tangent is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tangent.  If not, see <http://www.gnu.org/licenses/>.

    Contact:
        - David Stalnaker: david.stalnaker@gmail.com
        - Richard Zanibbi: rlaz@cs.rit.edu
"""

from __future__ import division
from collections import namedtuple

from tangent import SymbolTree

class Index:
    """
    A class to build an Index and search the index
    """
    def search_tex(self, tex):
        """
        Search the index for a given tex expression

        """
        return self.search(SymbolTree.parse_from_tex(tex))

    def add_all(self, trees):
        for t in trees:
            self.add(t)

    def add_directory(self, directory):
        """
        Add the expressions found in the index to the symbol tree

        :type directory: string
        :param directory: directory to search for expressions
        """
        self.add_all(SymbolTree.parse_directory(directory)[0])

    def second_pass(self):
        pass

Result = namedtuple('Result', ['latex', 'score', 'debug_info', 'links', 'expr_id'])

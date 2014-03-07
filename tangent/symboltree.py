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

import re
import os
import subprocess
import xml.etree.ElementTree as ET
import StringIO
from collections import deque, Counter
from sys import argv

ET.register_namespace('', 'http://www.w3.org/1998/Math/MathML')

class MathML:
    """
    List of ecognized tags
    """
    math = '{http://www.w3.org/1998/Math/MathML}math'
    mn = '{http://www.w3.org/1998/Math/MathML}mn'
    mo = '{http://www.w3.org/1998/Math/MathML}mo'
    mi = '{http://www.w3.org/1998/Math/MathML}mi'
    mtext = '{http://www.w3.org/1998/Math/MathML}mtext'
    mrow = '{http://www.w3.org/1998/Math/MathML}mrow'
    msub = '{http://www.w3.org/1998/Math/MathML}msub'
    msup = '{http://www.w3.org/1998/Math/MathML}msup'
    msubsup = '{http://www.w3.org/1998/Math/MathML}msubsup'
    munderover = '{http://www.w3.org/1998/Math/MathML}munderover'
    msqrt = '{http://www.w3.org/1998/Math/MathML}msqrt'
    mroot = '{http://www.w3.org/1998/Math/MathML}mroot'
    mfrac = '{http://www.w3.org/1998/Math/MathML}mfrac'
    mfenced = '{http://www.w3.org/1998/Math/MathML}mfenced'
    mover = '{http://www.w3.org/1998/Math/MathML}mover'
    munder = '{http://www.w3.org/1998/Math/MathML}munder'
    mpadded = '{http://www.w3.org/1998/Math/MathML}mpadded'
    none = '{http://www.w3.org/1998/Math/MathML}none'
    mstyle = '{http://www.w3.org/1998/Math/MathML}mstyle'
    mspace = '{http://www.w3.org/1998/Math/MathML}mspace'
    semantics = '{http://www.w3.org/1998/Math/MathML}semantics'

class UnknownTagException(Exception):
    """
    An exception to indicate unknown Mathml tag
    """
    def __init__(self, tag):
        self.tag = tag


class Symbol:
    """
    Symbol in a symbol tree
    """
    def __init__(self, tag, next=None, above=None, below=None, within=None):
        self.tag = tag
        self.next = next
        self.above = above
        self.below = below
        self.within = within
        self.id = None

    def build_repr(self, builder):
        """
        Build representation of symbol
        """
        builder.append('(')
        builder.append(self.tag)
        if self.next:
            builder.append(',next=')
            self.next.build_repr(builder)
        if self.above:
            builder.append(',above=')
            self.above.build_repr(builder)
        if self.below:
            builder.append(',below=')
            self.below.build_repr(builder)
        if self.within:
            builder.append(',within=')
            self.within.build_repr(builder)
        builder.append(')')

    def get_symbols(self):
        return SymbolIterator(self)

    def generate_ids(self, prefix=(0,)):
        self.id = prefix
        for child, v_dist in [(self.above, 1), (self.next, 0), (self.below, 2), (self.within, 3)]:
            if child:
                child.generate_ids(prefix + (v_dist,))

    def get_pairs(self):
        """
        Return the pairs in the symbol tree

        :rtype list
        :return list of symbols
        """
        def mk_helper(v_dist_diff):
            def helper(tup):
                right, h_dist, v_dist = tup
                return (self.tag, right.tag, h_dist + 1, v_dist + v_dist_diff, right.id)
            return helper

        ret = []
        for child, v_dist in [(self.above, 1), (self.next, 0), (self.below, -1), (self.within, 0)]:
            if child:
                ret.extend(map(mk_helper(v_dist), child.get_symbols()))
                ret.extend(child.get_pairs())
        return ret

    @classmethod
    def parse_from_mathml(cls, elem):
        """
        Parse symbol tree from mathml
        """
        if elem.tag == MathML.math:
            children = list(elem)
            if len(children) == 1:
                return cls.parse_from_mathml(children[0])
            elif len(children) == 0:
                return None
            else:
                raise Exception('math element with more than 1 child')
        if elem.tag == MathML.semantics:
            children = list(elem)
            if len(children) >= 1:
                return cls.parse_from_mathml(children[0])
            elif len(children) == 0:
                return None
        if elem.tag == MathML.mstyle:
            children = list(elem)
            if len(children) >= 1:
                return cls.parse_from_mathml(children[0])
            elif len(children) == 0:
                return None
        elif elem.tag == MathML.mrow:
            children = filter(lambda x: x is not None and x.tag != u'\u2062', map(cls.parse_from_mathml, elem))
            for i in range(1, len(children)):
                elem = children[i - 1]
                while elem.next:
                    elem = elem.next
                elem.next = children[i]
            return children[0]
        elif elem.tag == MathML.mn:
            return cls(elem.text if elem.text else '')
        elif elem.tag == MathML.mo:
            return cls(elem.text if elem.text else '')
        elif elem.tag == MathML.mi:
            return cls(elem.text if elem.text else '')
        elif elem.tag == MathML.mtext:
            return cls(elem.text if elem.text else '')
        elif elem.tag == MathML.mspace:
            return cls(' ')
        elif elem.tag == MathML.msub:
            children = map(cls.parse_from_mathml, elem)
            children[0].below = children[1]
            return children[0]
        elif elem.tag == MathML.msup:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
            return children[0]
        elif elem.tag == MathML.msubsup:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
            children[0].below = children[2]
            return children[0]
        elif elem.tag == MathML.munderover:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
            children[0].below = children[2]
            return children[0]
        elif elem.tag == MathML.mover:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
            return children[0]
        elif elem.tag == MathML.munder:
            children = map(cls.parse_from_mathml, elem)
            children[0].below = children[1]
            return children[0]
        elif elem.tag == MathML.msqrt:
            children = map(cls.parse_from_mathml, elem)
            if len(children) == 1:
                root = cls('root2')
                root.within = children[0]
                return root
            else:
                raise Exception('msqrt element with != 1 children')
        elif elem.tag == MathML.mroot:
            children = map(cls.parse_from_mathml, elem)
            if len(children) == 2:
                root = cls('root' + children[1].tag)
                root.within = children[0]
                return root
            else:
                raise Exception('mroot element with != 2 children')
        elif elem.tag == MathML.mfrac:
            children = map(cls.parse_from_mathml, elem)
            if len(children) == 2:
                s = cls('frac')
                s.above = children[0]
                s.below = children[1]
                return s
            else:
                raise Exception('frac element with != 2 children')
        elif elem.tag == MathML.mfenced:
            opening = cls(elem.attrib.get('open', '('))
            closing = cls(elem.attrib.get('close', '('))
            children = map(cls.parse_from_mathml, elem)
            separators = elem.attrib.get('separators', ',').split()

            row = [opening]
            if children:
                row.append(children[0])
            for i, child in enumerate(children[1:]):
                row.append(cls(separators[min(i, len(separators) - 1)]))
                row.append(child)
            row.append(closing)

            for i in range(1, len(row)):
                elem = row[i - 1]
                while elem.next:
                    elem = elem.next
                elem.next = row[i]
            return row[0]
        elif elem.tag == MathML.mpadded:
            children = filter(lambda x: x is not None and x.tag != u'\u2062', map(cls.parse_from_mathml, elem))
            for i in range(1, len(children)):
                elem = children[i - 1]
                while elem.next:
                    elem = elem.next
                elem.next = children[i]
            return children[0]
        elif elem.tag == MathML.none:
            return None
        else:
            raise UnknownTagException(elem.tag)

class SymbolIterator(object):
    """
    Iterator over a symbol tree
    """
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
        if elem.within:
            self.stack.append((elem.within, h_dist + 1, v_dist))
        return (elem, h_dist, v_dist)

class SymbolTree:
    """
    Symbol Tree manipulation and parsing

    Uses latexmlmath (http://dlmf.nist.gov/LaTeXML/index.html) to create the presentation mml

    """
    __slots__ = ['root', 'latex', 'mathml', 'document']

    def __init__(self, root):
        self.root = root
        self.root.generate_ids()

    def get_pairs(self, get_paths=False):
        """
        Return list of symbols

        :rtype: list
        :return list of symbols
        """
        if get_paths:
            pairs = []
            paths = []
            for s1, s2, dh, dv, path in self.root.get_pairs():
                pairs.append(('|'.join(map(unicode, [s1.replace('|', '!@!'), s2.replace('|', '!@!'), dh, dv]))))
                paths.append(''.join(map(unicode, path)))
            return pairs, paths
        else: 
            return ['|'.join(map(unicode, [s1.replace('|', '!@!'), s2.replace('|', '!@!'), dh, dv]))
                    for s1, s2, dh, dv, _
                    in self.root.get_pairs()]

    def get_symbols(self):
        return self.root.get_symbols()

    @classmethod
    def parse(cls, filename, missing_tags=None):
        """
        Extract symbols tree from file

        :type filename: string
        :param filename: directory to seach in

        :rtype: list(SymbolTree)
        :return list of Symbol trees
        """
        ext = os.path.splitext(filename)[1]
        if ext == '.tex':
            with open(filename) as f:
                return [cls.parse_from_tex(f.read())]
        elif ext in {'.xhtml', '.mathml', '.mml'}:
            return cls.parse_all_from_xml(filename, missing_tags=missing_tags)
        else:
            print('Unknown filetype for %s' % filename)
            return []

    @classmethod
    def parse_from_tex(cls, tex):
        """
        Parse expression from tex string using latexmlmath to convert ot presentation markup language


        :param tex tex string
        :type tex string

        :rtype SymbolTree
        :return SymbolTree
        """

        p = subprocess.Popen('latexmlmath -pmml - -', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=open('/dev/null', 'r'))
        (output, _) = p.communicate(input=tex)
        f = StringIO.StringIO(output)
        return cls.parse_all_from_xml(f)[0]

    @classmethod
    def parse_from_mathml_string(cls, mathml):
        """
        Parse expression from mathml string


        :param elem mathml string

        :rtype SymbolTree
        :return SymbolTree
        """
        f = StringIO.StringIO(mathml)
        return cls.parse_all_from_xml(f)[0]

    @classmethod
    def parse_from_mathml(cls, elem):
        """
        Parse expression from mathml


        :param elem mathml string

        :rtype SymbolTree
        :return SymbolTree

        """

        root = Symbol.parse_from_mathml(elem)
        tree = cls(root)
        tree.mathml = ET.tostring(elem)
        return tree

    @classmethod
    def parse_all_from_xml(cls, filename, missing_tags=None):
        """
        Parse expression from xml file


        :param filename Directory to search in
        :type  filename: string

        :rtype list(SymbolTree)
        :return list of Symbol trees found in file

        """
        trees = []
        for event, elem in ET.iterparse(filename):
            if event == 'end' and elem.tag == MathML.math:
                try:
                    tree = cls.parse_from_mathml(elem)
                    if 'alttext' in elem.attrib:
                        tree.latex = elem.attrib['alttext']
                    else:
                        tree.latex = ''
                    elem.tail = None
                    elem.attrib = {}
                    tree.mathml = ET.tostring(elem)
                    tree.document = filename
                    trees.append(tree)
                except UnknownTagException as e:
                    if missing_tags is not None:
                        missing_tags.update([e.tag])
                except Exception as e:
                    if missing_tags is not None:
                        missing_tags.update(['Unknown error: ' + e.message])
        return trees

    @classmethod
    def count_tags(cls, directory):
        tags = Counter()
        fullnames = []
        if os.path.isfile(directory):
            fullnames.append(directory)
        else:
            for dirname, dirnames, filenames in os.walk(directory):
                fullnames.extend([os.path.join(dirname, filename)
                    for filename
                    in filenames
                    if os.path.splitext(filename)[1] in ['.xhtml', '.xml', '.mathml']])

        for i, fullname in enumerate(fullnames):
            print('parsing %s (%d of %d)' % (fullname, i + 1, len(fullnames)))
            for event, elem in ET.iterparse(fullname):
                if event == 'end' and elem.tag.startswith('{http://www.w3.org/1998/Math/MathML}'):
                    tags.update([elem.tag[36:]])
        for tag, count in tags.most_common():
            print('%s, %d' % (tag, count))

    @classmethod
    def parse_directory(cls, directory):
        """
        Parse the symbols in the files in the directory

        :param directory Directory to search in
        :type  directory: string
        """
        missing_tags = Counter()
        fullnames = []
        if os.path.isfile(directory):
            fullnames.append(directory)
        else:
            for dirname, dirnames, filenames in os.walk(directory):
                fullnames.extend([os.path.join(dirname, filename) for filename in filenames])

        stats = {
            'num_documents': len(fullnames),
            'num_expressions': 0,
            'missing_tags': missing_tags
        }
        def get():
            for i, fullname in enumerate(fullnames):
                print('parsing %s (%d of %d)' % (fullname, i + 1, len(fullnames)))
                for t in cls.parse(fullname, missing_tags=missing_tags):
                    stats['num_expressions'] += 1
                    yield t
        return get(), stats


    def build_repr(self):
        builder = []
        self.root.build_repr(builder)
        builder = [b for b in builder if b]
        return u'SymbolTree(%s)' % u''.join(builder)

if __name__ == '__main__':
    trees = SymbolTree.parse_all(argv[1])
    print('%d expressions parsed' % len(trees))

import re
import os
import subprocess
import xml.etree.ElementTree as ET
import StringIO
from collections import deque, Counter
from sys import argv

ET.register_namespace('', 'http://www.w3.org/1998/Math/MathML')

class MathML:
    math = '{http://www.w3.org/1998/Math/MathML}math'
    mn = '{http://www.w3.org/1998/Math/MathML}mn'
    mo = '{http://www.w3.org/1998/Math/MathML}mo'
    mi = '{http://www.w3.org/1998/Math/MathML}mi'
    mrow = '{http://www.w3.org/1998/Math/MathML}mrow'
    msub = '{http://www.w3.org/1998/Math/MathML}msub'
    msup = '{http://www.w3.org/1998/Math/MathML}msup'
    msubsup = '{http://www.w3.org/1998/Math/MathML}msubsup'
    msqrt = '{http://www.w3.org/1998/Math/MathML}msqrt'
    mroot = '{http://www.w3.org/1998/Math/MathML}mroot'
    mfrac = '{http://www.w3.org/1998/Math/MathML}mfrac'
    mfenced = '{http://www.w3.org/1998/Math/MathML}mfenced'
    mover = '{http://www.w3.org/1998/Math/MathML}mover'
    munder = '{http://www.w3.org/1998/Math/MathML}munder'
    mpadded = '{http://www.w3.org/1998/Math/MathML}mpadded'
    semantics = '{http://www.w3.org/1998/Math/MathML}semantics'

class UnknownTagException(Exception):
    def __init__(self, tag):
        self.tag = tag


class Symbol:
    def __init__(self, tag, next=None, above=None, below=None):
        self.tag = tag
        self.next = next
        self.above = above
        self.below = below
        self.id = None

    def build_repr(self, builder):
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
        builder.append(')')

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
    def parse_from_mathml(cls, elem):
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
        elif elem.tag == MathML.mrow:
            children = filter(lambda x: x.tag != u'\u2062', map(cls.parse_from_mathml, elem))
            for i in range(1, len(children)):
                elem = children[i - 1]
                while elem.next:
                    elem = elem.next
                elem.next = children[i]
            return children[0]
        elif elem.tag == MathML.mn:
            return cls(elem.text)
        elif elem.tag == MathML.mo:
            return cls(elem.text)
        elif elem.tag == MathML.mi:
            return cls(elem.text)
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
        elif elem.tag == MathML.mover:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
            return children[0]
        elif elem.tag == MathML.munder:
            children = map(cls.parse_from_mathml, elem)
            children[0].below = children[1]
            return children[0]
        elif elem.tag == MathML.msqrt:
            raise Exception('msqrt unimplemented')
        elif elem.tag == MathML.mroot:
            raise Exception('mroot unimplemented')
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
            children = filter(lambda x: x.tag != u'\u2062', map(cls.parse_from_mathml, elem))
            for i in range(1, len(children)):
                elem = children[i - 1]
                while elem.next:
                    elem = elem.next
                elem.next = children[i]
            return children[0]
        else:
            raise UnknownTagException(elem.tag)

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

    __slots__ = ['root', 'num_pairs', 'mathml', 'document']

    def __init__(self, root):
        self.root = root
        self.num_pairs = len(list(self.get_pairs()))

    def get_pairs(self):
        return self.root.get_pairs()

    def get_symbols(self):
        return self.root.get_symbols()

    def get_html(self):
        return self.mathml

    @classmethod
    def parse(cls, filename, missing_tags=None):
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
        p = subprocess.Popen('latexmlmath -pmml - -', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=open('/dev/null', 'r'))
        (output, _) = p.communicate(input=tex)
        f = StringIO.StringIO(output)
        return cls.parse_all_from_xml(f)[0]

    @classmethod
    def parse_from_mathml(cls, elem):
        root = Symbol.parse_from_mathml(elem)
        root.generate_ids()
        tree = cls(root)
        tree.mathml = ET.tostring(elem)
        return tree

    @classmethod
    def parse_all_from_xml(cls, filename, missing_tags=None):
        trees = []
        for event, elem in ET.iterparse(filename):
            if event == 'end' and elem.tag == MathML.math:
                try:
                    tree = cls.parse_from_mathml(elem)
                    elem.tail = None
                    elem.attrib = {}
                    tree.mathml = ET.tostring(elem)
                    tree.document = filename
                    trees.append(tree)
                except UnknownTagException as e:
                    if missing_tags is not None:
                        missing_tags.update([e.tag])
                except Exception as e:
                    pass
                    #print(e.message)
        return trees

    @classmethod
    def count_tags(cls, directory):
        tags = Counter()
        fullnames = []
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
        trees = []
        missing_tags = Counter()
        fullnames = []
        for dirname, dirnames, filenames in os.walk(directory):
            fullnames.extend([os.path.join(dirname, filename) for filename in filenames])

        for i, fullname in enumerate(fullnames):
            print('parsing %s (%d of %d)' % (fullname, i + 1, len(fullnames)))
            trees.extend(cls.parse(fullname, missing_tags=missing_tags))
        stats = (len(fullnames), len(trees), missing_tags)
        return trees, stats


    def build_repr(self):
        builder = []
        self.root.build_repr(builder)
        builder = [b for b in builder if b]
        return u'SymbolTree(%s)' % u''.join(builder)

if __name__ == '__main__':
    trees = SymbolTree.parse_all(argv[1])
    print('%d expressions parsed' % len(trees))

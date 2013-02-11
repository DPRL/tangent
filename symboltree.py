import re
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import deque

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

    @classmethod
    def parse_from_mathml(cls, elem):
        if elem.tag == MathML.math:
            children = list(elem)
            if len(children) != 1:
                raise Exception('math element with != 1 children')
            else:
                return cls.parse_from_mathml(children[0])
        elif elem.tag == MathML.mrow:
            children = map(cls.parse_from_mathml, elem)
            for i in range(1, len(children)):
                children[i - 1].next = children[i]
            return children[0]
            
        elif elem.tag == MathML.mn:
            return cls(elem.text)
        elif elem.tag == MathML.mo:
            return cls(elem.text)
        elif elem.tag == MathML.mi:
            return cls(elem.text)
        elif elem.tag == MathML.msub:
            children = map(cls.parse_from_mathml, elem)
            children[0].above = children[1]
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
        elif elem.tag == MathML.msqrt:
            raise Exception('msqrt unimplemented')
        elif elem.tag == MathML.mroot:
            raise Exception('mroot unimplemented')
        elif elem.tag == MathML.mfrac:
            raise Exception('mfrac unimplemented')
        else:
            raise Exception('unknown tag %s' % elem.tag)
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
    def parse_from_mathml(cls, elem):
        root = Symbol.parse_from_mathml(elem)
        root.generate_ids()
        return cls(root)

    @classmethod
    def parse_all_from_xml(cls, filename):
        trees = []
        for event, elem in ET.iterparse(filename):
            if event == 'end' and elem.tag == MathML.math:
                try:
                    trees.append(cls.parse_from_mathml(elem))
                except Exception, e:
                    print(e.message)
        return trees

    @classmethod
    def parse(cls, iterator):
        root = Symbol.parse(deque(iterator))
        root.generate_ids()
        return cls(root)

    def __repr__(self):
        return 'SymbolTree({0})'.format(self.tex)


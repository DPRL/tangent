"""
    DPRL Math Symbol Recognizers
    Copyright (c) 2012-2014 David Stalnaker, Richard Zanibbi

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
from sys import argv, exit

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree

def index(directory):
    trees, stats = SymbolTree.parse_directory(directory)
    index = RedisIndex()
    index.add_all(trees)
    index.second_pass()

    print('')
    print('Added %d expressions from %d documents' % (stats['num_expressions'],
                                                      stats['num_documents']))
    print('Missing tags:')
    for tag, count in stats['missing_tags'].most_common():
        print('    %s (%d)' % (tag, count))

def second_pass():
    index = RedisIndex()
    index.second_pass()

def flush():
    index = RedisIndex()
    index.r.flushdb()

def print_help_and_exit():
    exit('Usage: python index.py {index|second_pass|flush} <directory> [<directory2> ..]')

if __name__ == '__main__':

    if len(argv) > 1:

        if argv[1] == 'index':
            for directory in argv[2:]:
                index(directory)
        elif argv[1] == 'second_pass':
            second_pass()
        elif argv[1] == 'flush':
            flush()
        else:
            print_help_and_exit()
    else:
        print(argv)
        print_help_and_exit()

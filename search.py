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

"""
    Console Script that can be used to query the index

"""

from sys import argv, exit, stdin
import json

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree


def search(config, query):
    """

    Search the redis index for the given latex expression

    :type config: Config
    :param config: Config object

    :rtype: dict
    :return: Dictionary containing "system". "query", "results"

    """
    index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
    results, _, _ = index.search_tex(query)
    return {
        'system': 'Tangent',
        'query': query,
        'results': [r.latex for r in results]
    }


def print_help_and_exit():
    """
    Prints Usage
    """
    exit('Usage: python search.py config_object query [query2, ...]')


if __name__ == '__main__':

    if len(argv) > 1:
        if argv[1] == 'help':
            print_help_and_exit()
        if len(argv) == 2:  #only one query
            config = import_string(argv[1])
            results = [search(config, query.strip()) for query in stdin.readlines()]
            print(json.dumps(results))
        else:  #multiple queries parsed
            config = import_string(argv[1])
            results = [search(config, query.strip()) for query in argv[2:]]
            print(json.dumps(results))
    else:
        print_help_and_exit()

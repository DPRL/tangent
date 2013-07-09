from sys import argv, exit, stdin
import json

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree

def search(config, query):
    index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
    results, _, _ = index.search_tex(query)
    return {
        'system': 'Tangent',
        'query': query,
        'results': [r.latex for r in results]
    }
        

def print_help_and_exit():
    exit('Usage: python search.py config_object query [query2, ...]')

if __name__ == '__main__':

    if len(argv) > 1:
        if argv[1] == 'help':
            print_help_and_exit()
        if len(argv) == 2:
            config = import_string(argv[1])
            results = [search(config, query.strip()) for query in stdin.readlines()]
            print(json.dumps(results))
        else:
            config = import_string(argv[1])
            results = [search(config, query.strip()) for query in argv[2:]]
            print(json.dumps(results))
    else:
        print_help_and_exit()

from sys import argv, exit

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree

def search(config, query):
    index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
    results, _, _ = index.search_tex(query)
    first = results[0]
    print(first[0])
        

def print_help_and_exit():
    exit('Usage: python search.py config_object query')

if __name__ == '__main__':

    if len(argv) > 2:
        if argv[1] == 'help':
            print_help_and_exit()
        else:
            config = import_string(argv[1])
            query = argv[2]
            search(config, query)
    else:
        print_help_and_exit()

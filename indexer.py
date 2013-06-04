from sys import argv, exit

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree
from config import FMeasureConfig, DistanceConfig, TfIdfConfig

def index(configs, directory):
    trees, (num_files, num_expressions, missing_tags) = SymbolTree.parse_directory(directory)
    for config in configs:
        index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
        index.add_all(trees)
        index.second_pass()

    print('')
    print('Added %d expressions from %d documents' % (num_expressions, num_files))
    print('Missing tags:')
    for tag, count in missing_tags.most_common():
        print('    %s (%d)' % (tag, count))

def second_pass(configs):
    for config in configs:
        index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
        index.second_pass()

def flush(configs):
    for config in configs:
        index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
        index.r.flushdb()

def print_help_and_exit():
    exit('Usage: python index.py {index|second_pass|flush} config_object <directory> [<directory2> ..]')

if __name__ == '__main__':

    if len(argv) > 2:
        if argv[2] == 'all':
            configs = [FMeasureConfig, DistanceConfig, TfIdfConfig]
        else:
            configs = [import_string(argv[2])]

        if argv[1] == 'index':
            for directory in argv[3:]:
                index(configs, directory)
        elif argv[1] == 'second_pass':
            second_pass(configs)
        elif argv[1] == 'flush':
            flush(configs)
        else:
            print('test1')
            print_help_and_exit()
    else:
        print(argv)
        print_help_and_exit()

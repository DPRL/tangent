from sys import argv, exit

from werkzeug.utils import import_string

from tangent import RedisIndex, SymbolTree

def index(config, directory):
    index = RedisIndex(db=config.DATABASE, ranker=config.RANKER)
    trees, (num_files, num_expressions, missing_tags) = SymbolTree.parse_directory(directory)
    index.add_all(trees)

    print('')
    print('Added %d expressions from %d documents' % (num_expressions, num_files))
    print('Missing tags:')
    for tag, count in missing_tags.most_common():
        print('    %s (%d)' % (tag, count))
        

def print_help_and_exit():
    exit('Usage: python index.py config_object <directory> [<directory2> ..]')

if __name__ == '__main__':

    if len(argv) > 2:
        if argv[1] == 'help':
            print_help_and_exit()
        else:
            config = import_string(argv[1])

            for directory in argv[2:]:
                index(config, directory)
    else:
        print_help_and_exit()

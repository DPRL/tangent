from tangent import RedisIndex, SymbolTree
from sys import argv, exit


def index(directory):
    index = RedisIndex()
    trees, (num_files, num_expressions, missing_tags) = SymbolTree.parse_directory(directory)
    index.add_all(trees)

    print('')
    print('Added %d expressions from %d documents' % (num_expressions, num_files))
    print('Missing tags:')
    for tag, count in missing_tags.most_common():
        print('    %s (%d)' % (tag, count))
        

def print_help_and_exit():
    exit('Usage: python index.py <directory> [<directory2> ..]')

if __name__ == '__main__':

    if len(argv) > 1:
        if argv[1] == 'help':
            print_help_and_exit()
        else:
            for directory in argv[1:]:
                index(directory)
    else:
        print_help_and_exit()

import time
from sys import argv, exit

from flask import Flask, render_template, request, make_response

from tangent import SymbolTree, RedisIndex

app = Flask(__name__)
index = RedisIndex()

def time_it(fn, *args):
    start = time.time()
    ret = fn(*args)
    end = time.time()
    return ((end - start) * 1000, ret)

@app.route('/')
def root():
    if 'query' in request.args:
        return query()
    else:
        return home()

@app.route('/stats')
def stats():
    return render_template('stats.html', stats=index.stats())

@app.route('/list')
def list_all():
    expressions = index.trees[:100]
    return render_template('list.html', expressions=expressions)

def home():
    return render_template('query.html')

def query():
    query = request.args['query']
    parse_time, tree = time_it(SymbolTree.parse_from_tex, query)
    search_time, results = time_it(lambda: list(index.search(tree)))
    return render_template('results.html', query=query, results=results, num_results=len(results), parse_time=parse_time, search_time=search_time)

@app.route("/listsize.png")
def listsize():
    import StringIO
    import random
 
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
 
    fig=Figure()
    fig.set_dpi = 100
    fig.set_size_inches(9, 12)
    fig.set_facecolor('w')
    ax=fig.add_subplot(211)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_title('Inverted list sizes')
    y = index.listsizes(filter_small=False)
    x = range(len(y))
    ax.plot(x, y, '-')

    ax=fig.add_subplot(212)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title('Inverted list sizes (log scale)')
    y = index.listsizes(filter_small=False)
    x = range(len(y))
    ax.plot(x, y, '-')

    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

def initialize(directory):
    trees, stats = SymbolTree.parse_directory(directory)
    index.add_all(trees)

def print_help_and_exit():
    exit('Usage: python mathsearch.py [port]')

if __name__ == '__main__':
    port = 9001

    if len(argv) > 1:
        if argv[1] == 'help':
            print_help_and_exit()
        else:
            try:
                port = int(argv[1])
            except:
                print_help_and_exit()

    app.run(port=port, host='0.0.0.0', debug=True)

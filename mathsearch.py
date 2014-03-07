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
Tangent web app is a Flask based App

Below are the routes and appropriates actions

/query=?: query page if query else home page
/random : retrieve a random expression and query

"""

import time
from sys import argv, exit
import os
import StringIO
from operator import itemgetter
import urlparse
import urllib

from flask import Flask, render_template, request, make_response

from tangent import SymbolTree, RedisIndex

app = Flask(__name__)
if len(argv) > 1:
    app.config.from_object(argv[1])
elif 'TANGENT_CONFIG' in os.environ:
    app.config.from_object(os.environ['TANGENT_CONFIG'])
else:
    print('Couldn\'t load config file')
    exit(0)

index = RedisIndex(db=app.config['DATABASE'], ranker=app.config['RANKER'])


def time_it(fn, *args):
    """
    Timing function
    """
    start = time.time()
    ret = fn(*args)
    end = time.time()
    return ((end - start) * 1000, ret)


@app.route('/')
def root():
    """
    Base route

    if params['query' is passed, query it
    else return to home page
    """
    if 'query' in request.args:
        query_expr = request.args['query']
        return query(query_expr)
    else:
        return home()


@app.route('/stats')
def stats():
    """
    [DEPRECATED]
    Display stats about redis index
    """
    return render_template('stats.html', stats=index.stats())


@app.route('/list')
def list_all():
    """
    [DEPRECATED]
    Return first 100 symbol tress
    """
    expressions = index.trees[:100]
    return render_template('list.html', expressions=expressions)


def home():
    """
    Home page
    """
    return render_template('query.html')


def query(query_expr):
    """
    Query the index given a query expression

    :type query_expr: string
    :param query_expr: query expression in tex and mathml
    """
    debug = 'debug' in request.args and request.args['debug'] == 'true'
    is_mathml = '<math' in query_expr
    if is_mathml:
        parse_time, tree = time_it(lambda f: SymbolTree.parse_from_mathml_string(f), query_expr)
    else:
        parse_time, tree = time_it(SymbolTree.parse_from_tex, query_expr)
    search_time, (results, num_results, pair_counts) = time_it(lambda: list(index.search(tree)))
    pair_count_str = u''

    #sort results by expression that share the most pair counts
    for p, c in sorted(pair_counts.items(), reverse=True, key=itemgetter(1)):
        pair_count_str += u'%s: %d, ' % (p, c)
    return render_template('results.html', query=query_expr, results=results, num_results=num_results,
                           pair_counts=pair_count_str, parse_time=parse_time, search_time=search_time, debug=debug)


def query_mathml(query_expr):
    """
    Query the index for the given mathml expression

    :type query_expr: string
    :param query_expr: query expression in  mathml

    """
    parse_time, tree = time_it(lambda f: SymbolTree.parse_all_from_xml(f)[0], query_expr)
    search_time, (results, num_results, pair_counts) = time_it(lambda: list(index.search(tree)))
    pair_count_str = u''
    for p, c in sorted(pair_counts.items(), reverse=True, key=itemgetter(1)):
        pair_count_str += u'%s: %d, ' % (p, c)
    return render_template('results.html', query='', results=results, num_results=num_results,
                           pair_counts=pair_count_str, parse_time=parse_time, search_time=search_time)


@app.route('/random')
def random():
    """
    Search the index for a random expression
    """
    latex = index.random()
    return query(latex)


@app.route("/listsize.png")
def listsize():
    """
    [DEPRECATED]
    Returns info about the inverted index
    """
    import StringIO
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    fig = Figure()
    fig.set_dpi = 100
    fig.set_size_inches(9, 12)
    fig.set_facecolor('w')
    ax = fig.add_subplot(211)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_title('Inverted list sizes')
    y = index.listsizes(filter_small=False)
    x = range(len(y))
    ax.plot(x, y, '-')

    ax = fig.add_subplot(212)
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

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.template_filter('urlencode')
def urlencode(uri, **query):
    return urllib.quote(uri)


app.jinja_env.globals['urlencode'] = urlencode


def initialize(directory):
    """
    parse all the expression found in the index

    :type directory:string
    :param directory: directory where to index expressions from
    """
    trees, stats = SymbolTree.parse_directory(directory)
    index.add_all(trees)


def print_help_and_exit():
    """
    Usage
    """
    exit('Usage: python mathsearch.py config_object')


if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == 'help':
            print_help_and_exit()

    #run app on host and port
    port = int(app.config['PORT'])
    host = app.config['HOST']
    app.run(port=port, host=host)

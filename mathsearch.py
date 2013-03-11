from flask import Flask, render_template, request
from invertedfile import PairIndex, SymbolIndex, CombinationIndex, SymbolTree
from sys import argv

app = Flask(__name__)
index = PairIndex()

@app.route('/')
def root():
    if 'query' in request.args:
        return query()
    else:
        return home()

@app.route('/initialize')
def initialize():
    trees, stats = SymbolTree.parse_directory(argv[1])
    index.add_all(trees)
    return render_template('initialized.html', stats=stats)

@app.route('/list')
def list_all():
    expressions = index.trees[:100]
    return render_template('list.html', expressions=expressions)

def home():
    return render_template('query.html')

def query():
    query = request.args['query']
    results = index.search_tex(query)
    return render_template('results.html', query=query, results=results, num_results=len(results))


if __name__ == '__main__':
    
    port = int(argv[2]) if len(argv) > 2 else 9001
    
    app.run(port=port, host='0.0.0.0', debug=True)

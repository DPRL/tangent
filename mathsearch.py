from flask import Flask, render_template, request
from invertedfile import PairIndex, SymbolIndex, CombinationIndex
import os
from sys import argv

app = Flask(__name__)
index = CombinationIndex()

@app.route('/')
def root():
    if 'query' in request.args:
        return query()
    else:
        return home()

def home():
    return render_template('query.html')

def query():
    query = request.args['query']
    results = sorted(index.search_tex(query), reverse=True, key=lambda x: x[1])
    results = map(lambda x: (x[0].get_tex(), x[1]), results)
    return render_template('results.html', query=query, results=results, num_results=len(results))

@app.route('/list')
def list_all():
    expressions = index.trees[:100]
    return render_template('list.html', expressions=expressions)

if __name__ == '__main__':

    for root, dirs, files in os.walk(argv[1]):
        for filename in files:
            with open(os.path.join(root, filename)) as f:
                index.add_tex(f.read())
    index.add_tex('a^2+b^2=c^2')
    index.add_tex('a^3+b^3=c^3')
    index.add_tex('x^2+y^2=z^2')

    print(list(index.search_tex('a^2+b^2=c^2')))

    #print('%d expressions in index' % len(index.trees))
    
    app.run(port=9001, host='0.0.0.0', debug=True)

from flask import Flask, render_template, request
from invertedfile import Symbol, SymbolTree, TreeIndex
import os
from sys import argv

app = Flask(__name__)
index = TreeIndex()

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
    t = SymbolTree.parse_from_tex(query)
    results = sorted(index.search(t), reverse=True, key=lambda x: x[1])
    results = map(lambda x: ('$' + index.trees[x[0]].tex + '$', x[1]), results)
    print(results)
    return render_template('results.html', query=query, results=results, num_results=len(results))

if __name__ == '__main__':

    for root, dirs, files in os.walk(argv[1]):
        for filename in files:
            with open(os.path.join(root, filename)) as f:
                tex = f.read()
                index.add(SymbolTree.parse_from_tex(tex))
    index.add(SymbolTree.parse_from_tex('a^2+b^2=c^2'))
    index.add(SymbolTree.parse_from_tex('a^3+b^3=c^3'))
    index.add(SymbolTree.parse_from_tex('x^2+y^2=z^2'))
    
    app.run(port=9001, host='0.0.0.0')

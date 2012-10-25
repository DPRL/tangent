from flask import Flask, render_template
from invertedfile import Symbol, SymbolTree, TreeIndex
app = Flask(__name__)
index = TreeIndex()

@app.route('/')
def hello():
    results = sorted(index.search(a), reverse=True, key=lambda x: x[1])
    results = map(lambda x: ('$' + index.trees[x[0]].tex + '$', x[1]), results)
    print(results)
    return render_template('results.html', results=results)

if __name__ == '__main__':

    a = SymbolTree.parse_from_tex('a^2+b^2=c^2')
    b = SymbolTree.parse_from_tex('a^3+b^3=c^3')
    c = SymbolTree.parse_from_tex('x^2+y^2=z^2')
    index.add(a)
    index.add(b)
    index.add(c)
    
    results = sorted(index.search(a), reverse=True, key=lambda x: x[1])

    for i, score in results:
        print (index.trees[i].tex, score)
    app.run(port=9001, host='0.0.0.0')

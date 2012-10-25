from flask import Flask, render_template
from invertedfile import Symbol, SymbolTree, TreeIndex
app = Flask(__name__)
index = TreeIndex()

@app.route('/')
def hello():
    return render_template('results.html')

if __name__ == '__main__':

    a = SymbolTree([
        Symbol('a', SymbolTree([
            Symbol('2')
        ])),
        Symbol('+'),
        Symbol('b', SymbolTree([
            Symbol('2')
        ])),
        Symbol('='),
        Symbol('c', SymbolTree([
            Symbol('2')
        ]))
    ], tex='a^2+b^2=c^2')
    b = SymbolTree([
        Symbol('a', SymbolTree([
            Symbol('3')
        ])),
        Symbol('+'),
        Symbol('b', SymbolTree([
            Symbol('3')
        ])),
        Symbol('='),
        Symbol('c', SymbolTree([
            Symbol('3')
        ]))
    ], tex='a^3+b^3=c^3')
    c = SymbolTree([
        Symbol('x', SymbolTree([
            Symbol('2')
        ])),
        Symbol('+'),
        Symbol('y', SymbolTree([
            Symbol('2')
        ])),
        Symbol('='),
        Symbol('z', SymbolTree([
            Symbol('2')
        ]))
    ], tex='x^2+y^2=z^2')
    index.add(a)
    index.add(b)
    index.add(c)
    
    results = sorted(index.search(a), reverse=True, key=lambda x: x[1])

    for i, score in results:
        print (index.trees[i].tex, score)
    app.run()

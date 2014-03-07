Tangent
=========
Author:  David Stalnaker: <david.stalnaker@gmail.com>



Overview:
======
Tangent is a Math search engine created by David Stalknaker as part of his Master's degree in Computer Science at RIT

Tangent allows the indexing and retrieval of math expressions using Symbol Pairs in Layout Trees.

Details  about the implementation can be found in his thesis:

[D. Stalnaker (2013) Math Expression Retrieval Using Symbol Pairs in Layout Trees. Master's Thesis, Rochester Institute of Technology (Computer Science), NY, USA (August 2013)](http://www.cs.rit.edu/~dprl/files/StalnakerMScThesisAug2013.pdf)



Dependencies
------------


Below are the external components used by Tangent

* [Latexml](http://dlmf.nist.gov/LaTeXML/index.html): a library to covert a Text expression to MathMl
* [MathJax](http://www.mathjax.org/): a javascript library used in displaying the math expressions in the results page
* [Redis](http://redis.io/): A Memory KeyValue store that is used as the index
* python 2.7

Python Modules:

* Redis: Module to connect from python to a redis datastorre
* [werkzeug](http://werkzeug.pocoo.org/):WSGI Utility Library
* [flask](http://flask.pocoo.org/): Microframework for Python

The above python modules can be installed using the command:

    pip install werkzeug redis flask



Running Tangent
======



To index a collection:
-----------------
    python indexer.py {index|flush} <directory> [<directory2> ..]
        index: index the formulas in the collection
        flush: empty the current index
        <directory>: directory or file containing tex and mathml documents containing formulas to index



To retrieve formulas:
-----------------
    python search.py config_object query [query2, ...]
        config_object: class name of Config object; ex: config.FMeasureConfig
        query: query expression in latex or mathml

        *config_object are defined in config.py and determine the host,port and score ranking

To run the webserver:
-----------------
    python mathsearch.py config_object
        config_object: class name of Config object; ex: config.FMeasureConfig

    The server will launch and be available on the port defined in the config object






* * *

* Visit the [DPRL page](http://www.cs.rit.edu/~dprl/) for more information about the lab and projects.

* This material is based upon work supported by the National Science Foundation under Grant No. IIS-1016815.
Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s)
and do not necessarily reflect the views of the National Science Foundation.
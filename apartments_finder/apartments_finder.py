__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'

import flask
from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run()

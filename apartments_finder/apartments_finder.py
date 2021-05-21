__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'

from data_collection import apartmentsdotcom
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/apartmentsdata')
def get_data():
    location = 'Philadelphia, PA'
    bedrooms = [1]
    filters = {'location': location,
               'bedrooms': bedrooms}
    data = apartmentsdotcom.get_apartmentsdotcom_data(filters)
    return render_template('apartmentsdata.html',  tables=[data.to_html(classes='data')], titles=data.columns.values)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

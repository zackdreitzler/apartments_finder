__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'


from data_collection import apartmentsdotcom
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/apartmentsdata', methods=['GET', 'POST'])
def get_data():
    """
    Gets data from apartmentsdotcom and passes it to the apartmentsdata page
    :return: rendered html page with apartments data
    """
    filters = {'location': request.form['city_filter'],
               'bedrooms': [int(request.form['bed_filter'])]}
    data = apartmentsdotcom.get_apartmentsdotcom_data(filters)
    tables = []
    titles = []
    if not data.empty:
        tables = [data.to_html()]
        titles = data.columns.values
    return render_template('apartmentsdata.html',  tables=tables, titles=titles)


@app.route('/')
def index():
    """
    Returns the index page of the website.
    :return: rendered html page of the index page.
    """

    with open('./config/usa_cities') as cities_file:
        cities = cities_file.readlines()

    return render_template('index.html', cities=cities)


if __name__ == '__main__':
    import sys
    debug = False
    port = 5000

    if len(sys.argv) > 3:
        print('More that 2 arguments passed through command line. Only the first 2 arguments will be used.')

    for arg in sys.argv[1:3]:
        if arg == '-d':
            debug = True
        else:
            try:
                port = int(arg)
            except ValueError:
                print(f'Failed to set port to: {arg}')

    app.run(debug=debug, port=port)
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import numpy as np
from flask import Flask, make_response, render_template
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

state_fips = '25'

# load state code dictionary
with open('data/state_codes.json', 'r') as infile:
    state_codes = json.load(infile)
# list of two-character state codes
states = list(state_codes.keys())

# load geolocation dataframe
geo_counts = pd.read_csv('data/geo_counts.csv', index_col=0)

# load geopandas county data
county_shapes = gpd.read_file('data/county_shapes.geojson')
county_shapes.set_index('GEOID', inplace=True)

@app.route('/')
def index():

    return render_template('map2.html')

@app.route('/plot.png')
def plot():

    fig, ax = plt.subplots(1, figsize=(20, 12))
    # choropleth for state by county
    county_shapes[county_shapes['STATEFP'] == state_fips].plot(
        ax=ax,
        column='report_counts',
        cmap='Reds',
        linewidth=0.5,
        edgecolor='0.1'
    )
    # geolocation mark
    # gpd.GeoDataFrame(geometry=geometry).plot(ax=ax, color='green', markersize=200, marker="*")
    ax.axis('off')
    fig.savefig('static/img/state_map.png')
    # plt.show()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == '__main__':
    app.run(debug=True)

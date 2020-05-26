# package imports
from flask import Flask, redirect, render_template, request, flash, url_for, Response, make_response
import pandas as pd
import geopandas as gpd
from config import Config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
# internal imports?
import json
import io

app = Flask(__name__)
# configuration settings
app.config.from_object(Config)

# load state code dict: 2-char to fips #
with open('data/state_codes.json', 'r') as infile:
    state_codes = json.load(infile)
# list of two-character state codes
states = list(state_codes.keys())

# load geolocation dataframe
geo_counts = pd.read_csv('data/geo_counts.csv', index_col=0)

# load geopandas county data
county_shapes = gpd.read_file('data/county_shapes.geojson')
county_shapes.set_index('GEOID', inplace=True)

# plot state choropleth function definition
def state_plot(geo_df, state_fips, geometry):
    fig, ax = plt.subplots(1, figsize=(20, 12))
    # choropleth for state by county
    geo_df[geo_df['STATEFP'] == state_fips].plot(
        ax=ax,
        column='report_counts',
        cmap='Reds',
        linewidth=0.5,
        edgecolor='0.1'
    )
    # geolocation mark
    gpd.GeoDataFrame(geometry=geometry).plot(ax=ax, color='green', markersize=200, marker="*")
    ax.axis('off')
    fig.savefig('static/img/state_map.png', bbox_inches='tight')


@app.route('/', methods=['GET', 'POST'])
def input():
    # get input data
    if request.method == 'POST':
        global state_fips
        global geometry
        # state input from input.html
        state_input = request.form['state_input']
        # city input from input.html
        city_input = request.form['city_input'].strip().title()
        geolocation = city_input + ', ' + state_input
        # validate geolocation
        if geolocation in geo_counts.index:
            # get state FIPS code
            state_fips = str(state_codes[state_input])
            # get county FIPS code
            county_fips = str(geo_counts.loc[geolocation, 'county_id']).zfill(5)
            # county name
            county_name = county_shapes.loc[county_fips, 'NAME']
            # geolocation report counts
            geo_count = int(geo_counts.loc[geolocation, 'report_counts'])
            # county report counts
            county_count = int(county_shapes.loc[county_fips, 'report_counts'])
            # state report counts
            state_count = int(county_shapes[county_shapes['STATEFP'] == state_fips]['report_counts'].sum())
            # geolocation coordinates
            latitude = [geo_counts.loc[geolocation, 'latitude']]
            longitude = [geo_counts.loc[geolocation, 'longitude']]
            # format as geopandas coordinate
            geometry = gpd.points_from_xy(longitude, latitude)
            # create choropleth map for state
            state_plot(county_shapes, state_fips, geometry)
            img = 'static/img/state_map.png'
            return render_template(
                'map.html',
                state_name=state_input,
                state_count=state_count,
                county_name=county_name,
                county_count=county_count,
                city_input=city_input,
                geo_count=geo_count,
                img=img
            )
        else:
            flash('Enter an incorporated US location')
            return redirect('/')
    else:
        return render_template('input.html', states=states)


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
    gpd.GeoDataFrame(geometry=geometry).plot(ax=ax, color='green', markersize=200, marker="*")
    ax.axis('off')
    fig.savefig('static/img/state_map.png')
    # plt.show()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == "__main__":
    app.run(debug=True)

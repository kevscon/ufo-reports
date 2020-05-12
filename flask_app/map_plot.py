import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import numpy as np

state_fips = '24'

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

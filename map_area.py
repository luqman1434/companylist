# NO CHORPPL;ETH
import math
import json
import warnings

import pandas as pd
import geopandas as gpd
import folium
from branca.element import Figure
from shapely.geometry import Point

import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

# Define the function to read the Excel file
def read_file(filename, sheetname):
    excel_file = pd.ExcelFile(filename)
    data_d = excel_file.parse(sheet_name=sheetname)
    return data_d

def plot_choropleth(map_obj, show_choropleth=True):
    if show_choropleth:
        choropleth = folium.Choropleth(
            geo_data=merged_gdf,
            name='choropleth',
            data=merged_gdf,
            columns=['NAME_2', 'count'],
            key_on='feature.properties.NAME_2',
            fill_color='RdYlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            threshold_scale=threshold_scale,
            line_color='black',
            legend_name='District Counts',
            highlight=False
        ).add_to(map_obj)
        folium.GeoJsonTooltip(fields=['NAME_1','NAME_2', 'count'], aliases=['State','District', 'Count']).add_to(choropleth.geojson)

# Main part of your code
if __name__ == '__main__':
    st.title('Available ITP companies in Malaysia')

    file_input = 'MMU ITP List 13_9_9_11.xlsx'
    geojson_file = "msia_district.geojson"

    text_load_state = st.text('Reading files ...')
    with open(geojson_file, encoding='utf-8', errors='ignore') as gj_f:
        geojson_data = gpd.read_file(gj_f)

    itp_list_state = read_file(file_input, 0)
    text_load_state.text('Reading files ... Done!') 

    map_size = Figure(width=800, height=600)
    map_my = folium.Map(location=[4.2105, 108.9758], zoom_start=6)
    map_size.add_child(map_my)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

    itp_list_state['geometry'] = itp_list_state.apply(lambda x: Point(x['map_longitude'], x['map_latitude']), axis=1)
    itp_list_state = gpd.GeoDataFrame(itp_list_state, geometry='geometry')

    # Add a sidebar for user input
    selected_states = st.multiselect('FILTER ITP COMPANIES BY STATE',itp_list_state['STATE'].unique())

    # Filter the data based on selected states
    ###filtered_data = itp_list_state[itp_list_state['STATE'].isin(selected_states)]

    joined_data = gpd.sjoin(geojson_data, selected_states, op="contains").groupby(["NAME_1", "NAME_2"]).size().reset_index(name="count")

    merged_gdf = geojson_data.merge(joined_data, on=["NAME_1", "NAME_2"], how="left")
    merged_gdf['count'].fillna(0, inplace=True)

    threshold_scale = [0, 1, 2, 4, 8, 16, 32, 64, 128, 200, 300, 400] 

    text_load_state.text('Plotting ...')
    for itp_data in filtered_data.to_dict(orient='records'):
        latitude = itp_data['map_latitude']
        longitude = itp_data['map_longitude']
        company_name = itp_data['Company name']
        popup_name = '<strong>' + str(itp_data['Company name']) + '</strong>\n' + str(itp_data['Company address'])
        if not math.isnan(latitude) and not math.isnan(longitude):
            folium.Marker(location=[latitude, longitude], popup=popup_name, tooltip=company_name).add_to(map_my)
    
    text_load_state.text('Plotting ... Done!')
    
    show_choropleth = st.checkbox("Show Choropleth", value=False)
    if show_choropleth:
        plot_choropleth(map_my)

    map_my.save('itp_area_map.html')
    p = open('itp_area_map.html')
    components.html(p.read(), 800, 480)

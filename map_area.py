#NO CHORPPL;ETH
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

# Main part of your code
if __name__ == '__main__':
    st.title('Available ITP companies in Malaysia')

    file_input = 'MMU ITP List 13_9_9_11.xlsx'

    text_load_state = st.text('Reading files ...')
    itp_list_state = read_file(file_input, 0)
    text_load_state.text('Reading files ... Done!') 

    # Get unique states from the Excel file
    unique_states = itp_list_state['STATE'].unique()

    # Add a checkbox to allow user to select states
    selected_states = st.multiselect('Select States', unique_states)

    map_size = Figure(width=800, height=600)
    map_my = folium.Map(location=[4.2105, 108.9758], zoom_start=6)
    map_size.add_child(map_my)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

    itp_list_state['geometry'] = itp_list_state.apply(lambda x: Point(x['map_longitude'], x['map_latitude']), axis=1)
    itp_list_state = gpd.GeoDataFrame(itp_list_state, geometry='geometry')

    # Filter ITP data by selected states
    itp_list_state_filtered = itp_list_state[itp_list_state['STATE'].isin(selected_states)]

    threshold_scale = [0, 1, 2, 4, 8, 16, 32, 64, 128, 200, 300, 400] 

    text_load_state.text('Plotting ...')
    for itp_data in itp_list_state_filtered.to_dict(orient='records'):
        latitude = itp_data['map_latitude']
        longitude = itp_data['map_longitude']
        company_name = itp_data['Company name']
        popup_name = '<strong>' + str(itp_data['Company name']) + '</strong>\n' + str(itp_data['Company address'])
        if not math.isnan(latitude) and not math.isnan(longitude):
            folium.Marker(location=[latitude, longitude], popup=popup_name, tooltip=company_name).add_to(map_my)
    
    text_load_state.text('Plotting ... Done!')

    map_my.save('itp_area_map.html')
    p = open('itp_area_map.html')
    components.html(p.read(), 800, 480)

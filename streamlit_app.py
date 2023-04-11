import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_folium import st_folium, folium_static
import folium
from geopy.distance import geodesic

st.set_page_config(layout="wide")
st.title('Property Wagon - HDB resale prices')

# SIDEBAR
st.sidebar.header('Tell us about the HDB you are interested in')
df_flat_type = pd.DataFrame({'flat_type': ['1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI-GENERATION']})
df_storey_range = pd.DataFrame({'storey_range': ['01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', '13 TO 15', '16 TO 18', '19 TO 21', '22 TO 24', '25 TO 27', '28 TO 30', '31 TO 33', '34 TO 36', '37 TO 39', '40 TO 42', '43 TO 45', '46 TO 48', '49 TO 51']})
address = st.sidebar.text_input('Address', 'Enter Address')
# town = st.sidebar.selectbox('Select Town', df_town['town'])
flat_type = st.sidebar.selectbox('Select number of rooms', df_flat_type['flat_type'])
storey_range = st.sidebar.selectbox('Select level of flat', df_storey_range['storey_range'])
# floor_area_sqm =
# lease_commence_date =
submit_button = st.sidebar.button('SUBMIT')

# LOAD DATA
recent_tnx = pd.read_csv('data/recent_tnx.csv')
medium_px = pd.read_csv('data/hdb_median_prices_by_town.csv')
amenities = pd.read_csv("data/amenities_list.csv")

def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    else:
        pass

def predict(address):
    # ENTER THE API FOR PREDICTED PRICE

    #  https://property-joycetoh-dpqqbevshq-as.a.run.app/predict?town=YISHUN&flat_type=EXECUTIVE&storey_range=01%20TO%2003&floor_area_sqm=164.0&flat_model=Apartment&lease_commence_date=1992&GDP=130024.7&HDB_resale_vol=2190.732478
    pred_px=600000
    return pred_px

def main():
    if submit_button:
        # DISPLAY MAP with RECENT TNX
        address_lat = getcoordinates(address)[0]
        address_long = getcoordinates(address)[1]

        map = folium.Map(location=[address_lat, address_long], zoom_start=17, control_scale=True)

        for index, location_info in recent_tnx.iterrows():
                        folium.CircleMarker(location=[location_info["Latitude"],location_info["Longitude"]],
                                            radius=5,
                                            color="crimson",
                                            fill=True,
                                            fill_color="crimson",
                                            popup=location_info[["flat_type", "storey_range", "remaining_lease_yr", "resale_price"]]).add_to(map)

        # ADD PREDICTION
        pred_price = predict(address)
        folium.Marker(location=[address_lat, address_long], popup= [address, flat_type, storey_range, pred_price]).add_to(map)

        st_map = folium_static(map, width=1400, height=700)
        st.write('Boundaries based on Master Plan 2014 Planning Area Boundary (No Sea)')

        # AMENITIES WITHIN 0.6 KM
        # Iterate over each row of the DataFrame and calculate the distance
        for index, row in amenities.iterrows():
            curr_lat = row['Latitude']
            curr_lon = row['Longitude']
            curr_pos = (curr_lat, curr_lon)
            ref_pos = (address_lat, address_long)
            distance = geodesic(curr_pos, ref_pos).km

            # Add the distance to the DataFrame as a new column
            amenities.at[index, 'Distance'] = distance

            # Create DataFrame where distance is less than 0.6 km
            nearby_amenities = amenities[amenities['Distance']<0.6]
            amenity=nearby_amenities[['Amenity','Type']].reset_index(drop=True)
                
        st.header('Nearby Amenities')
        st.write(amenity)

    else:
        # DISPLAY MAP default
        map = folium.Map(location=[1.35, 103.81], zoom_start=12, control_scale=True)
        choropleth = folium.Choropleth(geo_data='data/merged_gdf.geojson',
                                        data=medium_px,
                                        columns=('Name','4-ROOM'),
                                        key_on='feature.properties.Name',
                                        fill_opacity=0.3,
                                        legend_name='Medium Resale Price of 4-room HDB')
        choropleth.geojson.add_to(map)
        # Display Town Label
        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(fields=["Name", "4-ROOM"], labels=False))

        st_map = folium_static(map, width=1400, height=700)
        st.write('Boundaries based on Master Plan 2014 Planning Area Boundary (No Sea), showing Medium Resale Price of 4-room HDB in the town')

    # CREDITS
    st.write('Data Source from data.gov.sg, onemap.sg, and several other online sources')

if __name__ == "__main__":
    main()

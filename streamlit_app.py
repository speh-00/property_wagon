import streamlit as st
import pandas as pd
import requests
import numpy as np
from streamlit_folium import folium_static
import folium

st.set_page_config(layout="wide")
st.title('🎈 Property Wagon - HDB resale prices')

st.sidebar.header('Tell us about the HDB you are interested in')

df_flat_type = pd.DataFrame({'flat_type': ['1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI-GENERATION']})
df_storey_range = pd.DataFrame({'storey_range': ['01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', '13 TO 15', '16 TO 18', '19 TO 21', '22 TO 24', '25 TO 27', '28 TO 30', '31 TO 33', '34 TO 36', '37 TO 39', '40 TO 42', '43 TO 45', '46 TO 48', '49 TO 51']})

address1 = st.sidebar.text_input('Address', 'Enter Address')
flat_type1 = st.sidebar.selectbox('Select number of rooms', df_flat_type['flat_type'])
storey_range1 = st.sidebar.selectbox('Select level of flat', df_storey_range['storey_range'])
submit_button = st.sidebar.button('SUBMIT')

st.sidebar.header('Nearby Amenities')

if submit_button:
  train = 'api nearest train and distance'
  mall = 'api nearest mall and distance'
  hawker = 'api nearest hawker and distance'
  school = 'api nearest school and distance'
  supermarket = 'api nearest supermarket and distance'
  st.sidebar.write(train)
  st.sidebar.write(mall)
  st.sidebar.write(hawker)
  st.sidebar.write(school)
  
recent_tnx = pd.read_csv('data/recent_tnx.csv')
recent_tnx = recent_tnx[["Latitude", "Longitude", "flat_type", "storey_range", "remaining_lease_yr", "resale_price"]]

pred_price = "600,000"

def getcoordinates(address1):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal='+address1+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results'])>0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE']
    else:
        pass
    
address_lat = getcoordinates(address)[0]
address_long = getcoordinates(address)[1]

map = folium.Map(location=[address_lat, address_long], zoom_start=17, control_scale=True)

for index, location_info in recent_tnx.iterrows():
    folium.CircleMarker(location=[location_info["Latitude"],location_info["Longitude"]],
                         radius=5,
                         color="crimson", 
                         fill=True,
                         fill_color="crimson",
                         popup=location_info[["flat_type", "storey_range", "resale_price"]]).add_to(map)
    
folium.Marker(location=[address_lat, address_long], popup= [address1, flat_type1, storey_range1, pred_price]).add_to(map)

map
  

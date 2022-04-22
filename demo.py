import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from datetime import date
from datetime import datetime
import altair as alt


# Import data
data = pd.read_csv("output/result.csv")
data_copy = data.copy()

coordinatesDF = pd.read_csv("ua_coordinates.csv")
coordinatesDF.rename(columns={"lng": "lon"}, inplace=True)

# header
st.title('Russo-Ukraine Conflict Analysis')

# Configure Sidebar
st.sidebar.title("Data Selection")

st.sidebar.markdown(
    "Select the `Date` and `Hour` of interest to generate data visualization.")
selected_date = st.sidebar.date_input(
    "Select Date", datetime(2022, 3, 10)).strftime("%Y-%m-%d")
selected_hr = st.sidebar.slider(
    "Select hour", min_value=0, max_value=23, value=0, step=1)

if selected_date and selected_hr:
    hour = str(selected_hr*100).zfill(4)
    time = selected_date + " " + hour + "h"
    st.sidebar.write("You have selected: ", time)


st.markdown(
    "Visualize conflict areas in Ukraine based on twitter activity by date and hour.")
# Display Map
st.header("Map of top 5 cities")
st.write("Cities ranked by their respective percentage change of tweets per hour")
selectedDateHr = (data["Date"] == selected_date) & (
    data["Hour"] == selected_hr)

data = data[selectedDateHr].merge(coordinatesDF, left_on="EnglishTransCityName", right_on="EnglishTransCityName").sort_values(
    by='PctChange', ascending=False).iloc[0:5, :]
maxCount = data["PctChange"].max()
for row in data.itertuples():
    # count = row.PctChange/maxCount
    count = int(row.PctChange/maxCount*50)
    df = pd.DataFrame(
        np.random.randn(count, 2) / [10, 10] + [row.lat, row.lon],
        columns=['lat', 'lon'])

    data = data.append(df)
if data.empty:
  st.warning("No data available for chosen Date and Hour. Please select another.")
st.map(data=data, zoom=5)

# Display bar graph Histogram chart
st.header("Bar Chart of top 5 cities")
st.write("Cities ranked by their respective percentage change of tweets per hour")

data_bar = data_copy.copy()
data_bar = data_bar[(data_bar["Date"] == selected_date)
                    & (data_bar["Hour"] == selected_hr)]
data_bar = data_bar.sort_values(
    by=['PctChange'], ascending=False).reset_index().iloc[:5]
data_bar = data_bar.drop(['index', 'EnglishCityName'], axis=1)
if data_bar.empty:
    st.warning(
        "No data available for chosen Date and Hour. Please select another.")
else:
    st.write(data_bar)
    c = alt.Chart(data_bar).mark_bar().encode(
        x=alt.X('EnglishTransCityName', sort='-y'), y='PctChange')

    st.altair_chart(c, use_container_width=True)

# Displays the AG Grid
row0_spacer1, row0_1, row0_spacer2 = st.columns(
    (.1, 5, .1))
gb = GridOptionsBuilder.from_dataframe(
    data_copy, enableRowGroup=True, enableValue=True, enablePivot=True)
gb.configure_side_bar()
gb.configure_selection('single')
with row0_1:
    st.header("Raw Dataset")
    st.write("Result dataset generated from SoC cluster.")
    selection = AgGrid(
        data_copy,
        enable_enterprise_modules=True,
        gridOptions=gb.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,

    )

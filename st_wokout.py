import os
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Read in the public google sheet file
workout = conn.read()

#Catching any extra spaces when I typed in workouts 
workout["Exercise"] = workout["Exercise"].str.strip()

# Can use HTML to center header
st.markdown("<h1 style='text-align: center; color: black;'>Workout Site</h1>", unsafe_allow_html=True)
st.divider()


st.subheader("Workout filter")

# Get unique values from the column you want to filter on
filter_options = sorted(workout['Exercise'].unique().tolist())

# Create a selectbox with search functionality, use multiselect for selecting multiple options at once
filter_var = st.selectbox("Choose Workout:", filter_options)

# Filter the dataframe based on the selection
filtered_df = workout[workout['Exercise'] == filter_var]

st.dataframe(filtered_df, width=None, hide_index = True, column_order=['Timestamp', 'Exercise', 'Weight', 
                                                                    'Sets', 'Reps', 'Effort Level'])


st.subheader("Last 3 Workouts", divider="green")

# Filter to last 3 workout days 
workout['Timestamp'] = pd.to_datetime(workout['Timestamp'])
workout['date'] = workout['Timestamp'].dt.strftime('%b %d, %Y')

# Gets the last 3 items from our list
last_three_dates = workout['date'].unique().tolist()[-3:]

#Create the last 3 workout dates df to display
threeeee = workout[workout['date'].isin(last_three_dates)]  

#Displayed
st.dataframe(threeeee, width=None, hide_index = True, column_order=['date', 'Exercise', 'Weight', 
                                                                    'Sets', 'Reps', 'Effort Level'])

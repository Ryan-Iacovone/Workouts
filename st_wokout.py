import os
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Set streamlit page to automatically open in wide mode (helps for phone view) plus extra title details on browser
st.set_page_config(
    page_title="Workout Site",
    page_icon="💪",
    layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Read in the public google sheet file
workout = conn.read()

# Stripping any extra spaces in workouts column 
workout["Exercise"] = workout["Exercise"].str.strip()

link = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Can use HTML to center header
st.markdown("<h1 style='text-align: center; color: black;'>Workout Site</h1>", unsafe_allow_html=True)
# HTML with link
#st.markdown(f"<h1 style='text-align: center; color: black;'><a href='{link}'>Workout Site</a></h1>", unsafe_allow_html=True)
st.divider()


# Filtering single workouts 
st.subheader("Workout filter")

# Save unique exercises into list
filter_options = sorted(workout['Exercise'].unique().tolist())

# Create a selectbox with search functionality. Use multiselect for selecting multiple options at once
filter_var = st.selectbox("Choose Workout:", filter_options)

# Filter the dataframe based on user selection
filtered_df = workout[workout['Exercise'] == filter_var]

# Show filtered df in streamlit 
st.dataframe(filtered_df, width=None, hide_index = True, column_order=['Timestamp', 'Exercise', 'Weight', 
                                                                    'Sets', 'Reps', 'Effort Level'])


# Showing last 3 workouts 
st.subheader("Last 3 Workouts", divider="green")

# Change timestamp variable to datetime and then save it a date string 
workout['Timestamp'] = pd.to_datetime(workout['Timestamp'])
workout['date'] = workout['Timestamp'].dt.strftime('%b %d, %Y')

# Gets the last 3 dates I worked out
last_three_dates = workout['date'].unique().tolist()[-3:]

# Creates filtered df based off of the last three dates I worked out 
threeeee = workout[workout['date'].isin(last_three_dates)]  

# display the last 3 workouts df
st.dataframe(threeeee, width=None, hide_index = True, column_order=['date', 'Exercise', 'Weight', 
                                                                    'Sets', 'Reps', 'Effort Level'])


# Created a way to show effort level key and then hide it while clicking the same button

# Initialize the state
if 'show_content' not in st.session_state:
    st.session_state.show_content = False

# Define a function to toggle the state
def toggle_content():
    st.session_state.show_content = not st.session_state.show_content

# Create a button that toggles the content
if st.button('Show Effort Level Key', on_click=toggle_content):
    pass

# Display content based on the state
if st.session_state.show_content:
    effort_dict = {"4": "No effort", "5": "Easy", "6": "Moderate effort", "7": "Sweet spot, feel confident", "8": "Moderatly challenging but still completed", 
                   "9": "Very challenging, DNC", "10": "Extremely challenging, DNC, go down"}

    effort_df = pd.DataFrame(list(effort_dict.items()), columns=['Effort Rating', 'Description'], index=None)

    # Display effort key as a df in streamlit
    st.dataframe(effort_df, hide_index = True)
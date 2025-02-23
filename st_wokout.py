import pandas as pd
import datetime
import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar

# Set streamlit page to automatically open in wide mode (helps for phone view) plus extra title details on browser
st.set_page_config(
    page_title="Workout Site",
    page_icon="💪",
    layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Read in the public google sheet file
workout = conn.read()

# Pre emptive data cleaning stripping any extra spaces in workouts column and Timestamp variable to datetime
workout["Exercise"] = workout["Exercise"].str.strip()
workout['Timestamp'] = pd.to_datetime(workout['Timestamp'])

# Can use HTML to center header
st.markdown("<h1 style='text-align: center; color: black;'>Workout Site</h1>", unsafe_allow_html=True)
# HTML with link
#st.markdown(f"<h1 style='text-align: center; color: black;'><a href='{link}'>Workout Site</a></h1>", unsafe_allow_html=True)
st.divider()

####### Workout Calendar ####### 

# Grabs all unique workout dates and the number of exercises assoicated with each 
def prepare_calendar_data(workout_df):

    # Convert timestamps to datetime variable
    workout_df['Timestamp'] = pd.to_datetime(workout_df['Timestamp'])

    # Get unique dates when workouts occurred
    workout_dates = workout_df['Timestamp'].dt.date.unique() # dt.date changes it to just the date

    # Create calendar events
    calendar_events = []
    for date in workout_dates:
        # Counting the number of exercises completed on each unique date
        daily_workouts = len(workout_df[workout_df['Timestamp'].dt.date == date]) 
        
        # Create event dicitonary to add to calendar events
        event = {
            'title': f'{daily_workouts} Exercises',
            'start': date.isoformat(),
            'backgroundColor': '#28a745',  # Green color 
            'textColor': 'white',
            'display': 'background'  # This makes it show as a highlighted day
        }
        calendar_events.append(event)

    return calendar_events

# customizable options fo rhow to visual congfure the calendar
def create_calendar_config(events):
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "Today"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "events": events,
        "height": 400
    }
    
    return calendar_options


# Grabbing monthly exercise and workout statistics for this month and last month to be displayed
def get_monthly_stats(workout_df):

    # Get current and previous month
    current_date = pd.Timestamp.now() # Returns current datetime 
    current_month = current_date.strftime('%B') # Formats datetime as a month like "Febuary"
    prev_month = (current_date - pd.DateOffset(months=1)).strftime('%B')

    # Calculate workouts per month
    monthly_counts = workout_df.set_index('Timestamp').resample('ME').size()

    # Get last two months exercise counts based on the monthly_counts series above. Need to use 'dt.strftime('%B')' here because of how I formatted previous month above
    this_month = len(workout_df[workout_df['Timestamp'].dt.strftime('%B') == current_month])
    last_month = len(workout_df[workout_df['Timestamp'].dt.strftime('%B') == prev_month])
    
    return this_month, last_month, current_month, prev_month

# Get monthly statistics and displays them in a card like format 
this_month, last_month, current_month, prev_month = get_monthly_stats(workout)

col1, col2, col3 = st.columns(3)

# Exercises this month
with col1:
    st.metric(f"{current_month} Workouts", this_month, f"{this_month - last_month} vs last month") # st.metric takes (label, value, delta/change)

# Monthly target for exercises  
with col2:
    days_in_month = pd.Timestamp.now().daysinmonth
    st.metric("Monthly Target", days_in_month // 2, f"{this_month - (days_in_month // 2)} from target")

# Average exercises per day
with col3:
    if this_month > 0:
        avg_workouts = workout[workout['Timestamp'].dt.strftime('%B') == current_month]['Exercise'].count() / this_month
        st.metric("Avg Exercises/Day", f"{avg_workouts:.1f}")

with st.expander("📅 Workout Calendar", expanded=False):
    st.write("Days highlighted in green show when you worked out!")
    
    # Prepare and display calendar
    calendar_events = prepare_calendar_data(workout)
    calendar_options = create_calendar_config(calendar_events)
    calendar(calendar_options)


####### Single workouts filter ####### 
with st.expander("🎯 Specific Exercise Filter", expanded=True):
    st.subheader("Specific Exercise Filter")

    # Save unique exercises into list
    filter_options = sorted(workout['Exercise'].unique().tolist())

    # Create a selectbox with search functionality. Use multiselect for selecting multiple options at once
    filter_var = st.selectbox("Choose Exercise:", filter_options)

    # Filter the dataframe based on user selection
    filtered_df = workout[workout['Exercise'] == filter_var]

    # Show filtered df in streamlit, show index column for later filtering
    st.dataframe(filtered_df, width=None, hide_index = False, column_order=[ 'Index', 'Timestamp', 'Exercise', 'Weight', 
                                                                        'Sets', 'Reps', 'Effort Level'])


####### Extracting the core name of the excerise #######
with st.expander("💪 Muscle Group Analysis", expanded=False):
    st.subheader("Muscle Group Anlaysis")

    # need the .str[0] because I'm applying the split method to a pandas series
    workout["core_name"] = workout["Exercise"].str.split(" ").str[0]

    # Show last 4 -5 workouts by muscle group

    # Save unique exercises into list
    core_options = sorted(workout['core_name'].unique().tolist())

    # Create a selectbox with search functionality. Use multiselect for selecting multiple options at once
    core_var = st.selectbox("Choose Workout Group:", core_options)

    # Filter the dataframe based on user selection and grab the last 6 workouts in that core area
    core_filtered = workout[workout['core_name'] == core_var].tail(6)

    # Show filtered df in streamlit 
    st.dataframe(core_filtered, width=None, hide_index = True, column_order=['Timestamp', 'Exercise', 'Weight', 
                                                                        'Sets', 'Reps', 'Effort Level'])


####### Last 3 times I worked out ####### 
with st.expander("📅 Last 3 Workouts", expanded=False):
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


######## Comment Extractor ########
with st.expander("📝 Comment Extractor", expanded=False):
    st.subheader("Comment Extractor")

    number = st.number_input("Pick a number", value=50, step=1, min_value=0, max_value=max(workout.index))

    filtered_index = pd.DataFrame(workout.iloc[[number]])  

    # Show filtered df in streamlit 
    st.dataframe(filtered_index, width=None, hide_index = False, column_order=['Timestamp', 'Exercise', 'Notes:'])


######## Effort level key and then hide it while clicking the same button ########

# Initialize the state
if 'show_content' not in st.session_state:
    st.session_state.show_content = False

# Define a function to toggle the state
def toggle_content():
    st.session_state.show_content = not st.session_state.show_content

# Adding in some hrml to create a beak
st.markdown("<br>", unsafe_allow_html=True)

# Create a button that toggles the content
if st.button('Show Effort Level Key', on_click=toggle_content):
    pass

# Display content based on the state
if st.session_state.show_content:
    effort_dict = {
                "4": "No effort 😴",
                "5": "Easy 🌟",
                "6": "Moderate effort 💪",
                "7": "Sweet spot, feel confident 🎯",
                "8": "Moderately challenging but still completed 🔥",
                "9": "Very challenging, DNC ⚠️",
                "10": "Extremely challenging, DNC, go down ⛔"
            }
    

    effort_df = pd.DataFrame(list(effort_dict.items()), columns=['Effort Rating', 'Description'], index=None)

    # Display effort key as a df in streamlit
    st.dataframe(effort_df, hide_index = True)
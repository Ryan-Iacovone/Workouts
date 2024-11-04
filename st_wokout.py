import os
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = st.secrets["sheet_id"]

def read_in_google_sheet():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = st.secrets["token"]
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  """if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
"""
  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range="Form Responses 1")
        .execute()
    )
    values = result.get("values", [])

    df = pd.DataFrame(values[1:], columns=values[0], index=None)
    return df

  except HttpError as err:
    print(err)

workout = read_in_google_sheet()

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

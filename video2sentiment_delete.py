# Importing necessary libraries
import streamlit as st
#st.set_page_config(layout="wide")
import streamlit.components.v1 as components
import requests
import json
import os
import pyodbc
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from getaccesstoken import get_access_token
import pandas as pd
from dotenv import dotenv_values
import sys
import plotly.express as px
from openai import AzureOpenAI
from pprint import pprint
from SessionState import get
from urllib.parse import quote
from sqlalchemy import create_engine
import urllib
from datetime import date
from IPython.display import display
import ipywidgets as widgets
import concurrent.futures

# Importing necessary modules from VideoIndexerClient
from VideoIndexerClient.Consts import Consts
from VideoIndexerClient.VideoIndexerClient import VideoIndexerClient

# Setting the page layout to wide
  

# Loading environment variables
config = dotenv_values(".env")
subscription_key = os.getenv('SUBSCRIPTION_KEY')
location = os.getenv('LOCATION')
account_id = os.getenv('ACCOUNT_ID')
api_url = os.getenv('API_URL')
headers = {"Ocp-Apim-Subscription-Key": subscription_key}

config = dotenv_values(".env")

# Getting necessary configuration details from environment variables
AccountName = config.get('AccountName')
ResourceGroup = config.get('ResourceGroup')
SubscriptionId = config.get('SubscriptionId')
Location = config.get('LOCATION')

ApiVersion = '2024-01-01'
ApiEndpoint = 'https://api.videoindexer.ai'
AzureResourceManager = 'https://management.azure.com'

# Creating and validating consts
consts = Consts(ApiVersion, ApiEndpoint, AzureResourceManager, AccountName, ResourceGroup, SubscriptionId,Location)

# Creating Video Indexer Client
client = VideoIndexerClient()

# Getting access tokens (arm and Video Indexer account)
client.authenticate_async(consts)

# Establishing a connection to the database
odbc_conn_str = os.getenv('ODBC_CONN_STR')
conn = pyodbc.connect(odbc_conn_str)

df = pd.DataFrame({
    'speech_entity': ['entity1', 'entity2', 'entity3', 'entity1', 'entity2'],
    'speech_emotion': ['happy', 'sad', 'neutral', 'happy', 'sad']
})

def delete_video(video_id, access_token):
        # Fetch environment variables
    print("start the upload VI process")
    subscription_key = os.getenv('SUBSCRIPTION_KEY')
    location = os.getenv('LOCATION')
    account_id = os.getenv('ACCOUNT_ID')
    api_url = os.getenv('API_URL')
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    download_path = os.getenv('DOWNLOAD_PATH')
    
    # Get access token
    #description = quote(video_name)
    access_token = get_access_token()
    #print("the access token is: "+ access_token)


# Function to get all video ids
def get_all_video_ids():
    url = f'{api_url}/{location}/Accounts/{account_id}/Videos'
    params = {'accessToken': get_access_token()}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        #st.write(response.json())
        return response.json()
    else:
        response.raise_for_status()


def seconds_to_hh_mm(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%02d:%02d" % (hours, minutes)

def fetch_thumbnail(video_id):
    url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id['id']}/Thumbnails/{video_id['thumbnailId']}"
    params = {'accessToken': get_access_token(), 'format': 'Jpeg'}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        duration = seconds_to_hh_mm(video_id['durationInSeconds'])
        return True, response.content, str(video_id['description']), video_id['id'], duration
    else:
        response.raise_for_status()
    return False, None, None, None, None

def get_all_thumbnail_ids(video_ids):
    thumbnail_ids = []
    max_cols_per_row = 4
    rows = [st.columns(max_cols_per_row) for _ in range((len(video_ids) + max_cols_per_row - 1) // max_cols_per_row)]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_thumbnail, video_id) for video_id in video_ids]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                success, image, description, video_id, duration = future.result()
                if success:
                    row = rows[i // max_cols_per_row]
                    col = row[i % max_cols_per_row]
                    col.image(image)
                    col.write(f"Descriptin: {description}")
                    col.write(f"Duration: {duration}")
                    if col.button(f'Click for image {i}'):
                        return True, video_id
            except Exception as e:
                print(f"Exception occurred: {e}")
    return False, None




def fetch_speech_general_info(video_id):
    print(f"Video ID: {video_id}")  # Debug Step 1 & 2
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT speech_date, speech_speaker, speech_description FROM speech_general_info WHERE speech_vi_video_id = ?", (str(video_id),))
    except Exception as e:
        print(f"Database error: {e}")  # Debug Step 4
    row = cursor.fetchone()
    print(f"Query Result: {row}")  # Debug Step 3
    if row is None:
        return None
    return {'date': row[0], 'speaker': row[1], 'description': row[2]}  # return a dictionary


# Main function
def main():

    api_key = os.getenv('AZURE_OPENAI_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    odbc_conn_str = os.getenv('ODBC_CONN_STR')



    # Establish a connection to the database
    conn = pyodbc.connect(odbc_conn_str)  
    video_ids = get_all_video_ids()  
    names = ["Hasan Nasrallah", "Joy Biden", "Mohammed Bin Salman"]  
    selected_name = st.sidebar.selectbox('Select a name', names)  
    filtered_videos = [video for video in video_ids['results'] if video.get('metadata') == selected_name]  
    image_button_clicked, video_id = get_all_thumbnail_ids(filtered_videos)  
      
    if image_button_clicked:  
        speech_vi_video_id=video_id
            # Fetch speech data
        speech_data = fetch_speech_general_info(speech_vi_video_id)
        # Convert speech_data to a DataFrame
        df = pd.DataFrame(speech_data, columns=['Column1', 'Column2', 'Column3'])

        # Display the DataFrame as a table in Streamlit
        st.table(df)
        
        if speech_data is not None:
            speech_date = speech_data['date']
            speech_speaker = speech_data['speaker']
            speech_description = speech_data['description']
            



        

              

          

  
# Ensure the main function is called only when the script is executed directly  
if __name__ == "__main__":  
    main()  
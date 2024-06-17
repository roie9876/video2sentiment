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

def delete_video(video_id):
        # Fetch environment variables
    print("start the delete video id")
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
    upload_url = f"https://api.videoindexer.ai/{location}/Accounts/{account_id}/Videos/{video_id}?accessToken={access_token}"
    #st.write("The upload url is: "+ upload_url) 
    response = requests.delete(upload_url)
    #st.write(response)

    # Check if there was an error uploading the video
    if "ErrorType" in response:
        
        print(f"Error delete video: {response['Message']}")
    else:
        print(f"Video deleted successfully video: "+ video_id)
        st.write(f"Video deleted successfully video: "+ video_id)


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
    video_ids_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_thumbnail, video_id) for video_id in video_ids]
        for i, future in enumerate(futures):
            try:
                success, image, description, video_id, duration = future.result()
                if success:
                    row = rows[i // max_cols_per_row]
                    col = row[i % max_cols_per_row]
                    col.image(image)
                    col.write(f"Description: {description}")
                    col.write(f"Duration: {duration}")
                    col.write(f"Video ID: {video_id}")
                    if col.button(f'Click for video {video_id}'):
                        return True, video_id
                    video_ids_list.append(video_id)
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
        if video_id is not None and video_id != '':
            speech_vi_video_id=video_id
            

            
            
                # Fetch speech data
            
            # Convert speech_data to a DataFrame
            

            #delete the video_id
            #delete_video(speech_vi_video_id)
            # delete all data from the database based on the video_id from all tables
            odbc_conn_str = os.getenv('ODBC_CONN_STR')
            conn = pyodbc.connect(odbc_conn_str)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM speech_general_info WHERE speech_vi_video_id = ?", (speech_vi_video_id,))
                cursor.execute("DELETE FROM speech_general_hebrew_language WHERE speech_vi_video_id = ?", (speech_vi_video_id,))
                cursor.execute("DELETE FROM speech_general_original_language WHERE speech_vi_video_id = ?", (speech_vi_video_id,))
                cursor.execute("DELETE FROM speech_sentiment_hebrew_language WHERE speech_vi_video_id = ?", (speech_vi_video_id,))
                cursor.execute("DELETE FROM speech_sentiment_original_language WHERE speech_vi_video_id = ?", (speech_vi_video_id,))
                conn.commit()
            except Exception as e:
                print(f"Database error: {e}")
            



        

              

          

  
# Ensure the main function is called only when the script is executed directly  
if __name__ == "__main__":  
    main()  
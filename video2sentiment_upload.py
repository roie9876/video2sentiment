import os
from pytube import YouTube
from urllib.parse import quote
import time
import re
import requests
import codecs
import streamlit as st
from openai import AzureOpenAI
from urllib.parse import quote
import time
import json
import pandas as pd
import datetime
import pyodbc
import pandas as pd
import urllib
import subprocess
from django.core.files.uploadedfile import UploadedFile

from sqlalchemy import create_engine




# Import the function from getaccesstoken.py
from getaccesstoken import get_access_token








@st.cache_data


def download_youtube_video(youtube_url):
    if not youtube_url:
        print("No YouTube URL provided.")
        return
    print("the youtube url is: "+ youtube_url)
    video_name = None
    yt = YouTube(youtube_url)
    video = yt.streams.first()
    video_name = video.title
    download_path = "/Users/robenhai/video2sentiment/videos"
    if len(video_name) > 80:
        video_name = video_name[:80]  
        video_name = re.sub(r'\W+', '', video_name)  
        video_name = video_name + ".mp4" 
        video.download(download_path, filename=video_name) 
        print("the video name is: "+ video_name)
        print("finished downloading the video")
    else:
        video_name = re.sub(r'\W+', '', video_name)  
        video_name = video_name + ".mp4" 
        video.download(download_path, filename=video_name) 
    return video_name

# Your code to create the YouTube URL input and the "Upload Video" button
youtube_url = st.text_input('Enter YouTube URL')
upload_button = st.button('Upload Video')

if upload_button:
    # Only download the YouTube video after the "Upload Video" button is clicked
    video_name = download_youtube_video(youtube_url)
    if video_name is None:
        st.write("Failed to download the video.")
    else:
        st.write("Finished downloading the video, the video name is: " + video_name)

@st.cache_data
# def upload_to_video_indexer(video_name,language_code,speech_speaker,description):
#     # Fetch environment variables
#     print("start the upload VI process")
#     subscription_key = os.getenv('SUBSCRIPTION_KEY')
#     location = os.getenv('LOCATION')
#     account_id = os.getenv('ACCOUNT_ID')
#     api_url = os.getenv('API_URL')
#     headers = {"Ocp-Apim-Subscription-Key": subscription_key}
#     download_path = os.getenv('DOWNLOAD_PATH')
    
#     # Get access token
#     #description = quote(video_name)
#     print ("the video name is: "+ video_name)
#     access_token = get_access_token()
#     print("the access token is: "+ access_token)


#      # Free text to be displayed in the Streamlit UI
#     original_text = '<p style="color:red;font-weight:bold;">This is original text from video.</p>'  
#     # Construct the upload URL
#     indexingPreset = 'AdvancedVideo'
    
#     excludedAI='Celebrities,DetectedObjects,Emotions,Entities,Faces,Keywords,KnownPeople,OCR,RollingCredits,ShotType,Speakers,Topics'

#     upload_url = f"{api_url}/{location}/Accounts/{account_id}/Videos?accessToken={access_token}&name={video_name}&description={description}&language={language_code}&metadata={speech_speaker}&excludedAI={excludedAI}"

#     # Define the path to the video file
#     video_path = f"/Users/robenhai/video2sentiment/videos/{video_name}"

#     # Open the video file and send a POST request to the upload URL
#     with open(video_path, "rb") as video_file:
#         response = requests.post(upload_url, files={"file": video_file})
#         response_json = response.json()
#         print("The response of upload to VI is:" + json.dumps(response_json))

#         # Check if there was an error uploading the video
#         if "ErrorType" in response_json:
#             print(f"Error uploading video: {response_json['Message']}")
#         else:
#             video_id = response_json["id"]
            
#     # Initialize retry parameters
#     max_retries = 10000
#     retries = 0

#     # Check the video index status until it's processed or max retries reached
# # Check the video index status until it's processed or max retries reached
#     while retries < max_retries:
#         # Get the video index status
#         index_status_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Index?accessToken={access_token}"
#         index_status_response = requests.get(index_status_url)
#         index_status = index_status_response.json()

#         # If the video has finished indexing, break the loop
#         for video in index_status["videos"]:
#             if video["state"] == "Processed":
#                 break
#         else:
#             # Wait for a while before checking again
#             time.sleep(10)  # Wait for 10 seconds
#             st.write("the video is processing")
#             print("the video is processing")
#             retries += 1
#             continue
#         break

#     # If max retries reached, print a message
#     if retries == max_retries:
#         st.write("Video processing took too long. Please check the video status manually.")
#         print("Video processing took too long. Please check the video status manually.")
#     else:
#         return video_id

def upload_to_video_indexer(video_name, language_code, speech_speaker, description, source='youtube'):
    
    if video_name is None or not isinstance(video_name, str):
        print("Invalid video name provided.")
        return
    # Fetch environment variables
    print("start the upload VI process")
    subscription_key = os.getenv('SUBSCRIPTION_KEY')
    location = os.getenv('LOCATION')
    account_id = os.getenv('ACCOUNT_ID')
    api_url = os.getenv('API_URL')
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    download_path = os.getenv('DOWNLOAD_PATH')

    # Get access token
    print ("the video name is: "+ video_name)
    access_token = get_access_token()
    print("the access token is: "+ access_token)

    # Free text to be displayed in the Streamlit UI
    original_text = '<p style="color:red;font-weight:bold;">This is original text from video.</p>'  

    # Construct the upload URL
    indexingPreset = 'AdvancedVideo'
    excludedAI='Celebrities,DetectedObjects,Emotions,Entities,Faces,Keywords,KnownPeople,OCR,RollingCredits,ShotType,Speakers,Topics'
    upload_url = f"{api_url}/{location}/Accounts/{account_id}/Videos?accessToken={access_token}&name={video_name}&description={description}&language={language_code}&metadata={speech_speaker}&excludedAI={excludedAI}"

    # Define the path to the video file
    if source == 'youtube':
        video_path = f"{download_path}/{video_name}"
    else:
        video_path = f"/Users/robenhai/video2sentiment/videos/{video_name}"

    # Open the video file and send a POST request to the upload URL
    with open(video_path, "rb") as video_file:
        response = requests.post(upload_url, files={"file": video_file})
        response_json = response.json()
        print("The response of upload to VI is:" + json.dumps(response_json))

        # Check if there was an error uploading the video
        if "ErrorType" in response_json:
            print(f"Error uploading video: {response_json['Message']}")
        else:
            video_id = response_json["id"]

    # Initialize retry parameters
    max_retries = 10000
    retries = 0

    # Check the video index status until it's processed or max retries reached
    while retries < max_retries:
        # Get the video index status
        index_status_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Index?accessToken={access_token}"
        index_status_response = requests.get(index_status_url)
        index_status = index_status_response.json()

        # If the video has finished indexing, break the loop
        for video in index_status["videos"]:
            if video["state"] == "Processed":
                break
        else:
            # Wait for a while before checking again
            time.sleep(10)  # Wait for 10 seconds
            st.write("the video is processing")
            print("the video is processing")
            retries += 1
            continue
        break

    # If max retries reached, print a message
    if retries == max_retries:
        st.write("Video processing took too long. Please check the video status manually.")
        print("Video processing took too long. Please check the video status manually.")
    else:
        return video_id
    

def upload_to_video_indexer_fromlocalfile(uploaded_file, language_code, speech_speaker, speech_description):
    

    # Fetch environment variables
    print("start the upload VI process")
    subscription_key = os.getenv('SUBSCRIPTION_KEY')
    location = os.getenv('LOCATION')
    account_id = os.getenv('ACCOUNT_ID')
    api_url = os.getenv('API_URL')
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    download_path = os.getenv('DOWNLOAD_PATH')
    video_name = uploaded_file.name
    # Get access token

    access_token = get_access_token()
    print("the access token is: "+ access_token)

    # Free text to be displayed in the Streamlit UI
    original_text = '<p style="color:red;font-weight:bold;">This is original text from video.</p>'  

    # Construct the upload URL
    indexingPreset = 'AdvancedVideo'
    excludedAI='Celebrities,DetectedObjects,Emotions,Entities,Faces,Keywords,KnownPeople,OCR,RollingCredits,ShotType,Speakers,Topics'
    upload_url = f"{api_url}/{location}/Accounts/{account_id}/Videos?accessToken={access_token}&name={video_name}&description={speech_description}&language={language_code}&metadata={speech_speaker}&excludedAI={excludedAI}"

    # Define the path to the video file
    video_path = os.path.join('/Users/robenhai/video2sentiment/videos', uploaded_file.name)
    # Open the video file and send a POST request to the upload URL
    with open(video_path, "rb") as video_file:
        response = requests.post(upload_url, files={"file": video_file})
        response_json = response.json()
        print("The response of upload to VI is:" + json.dumps(response_json))

        # Check if there was an error uploading the video
        if "ErrorType" in response_json:
            print(f"Error uploading video: {response_json['Message']}")
        else:
            video_id = response_json["id"]

    # Initialize retry parameters
    max_retries = 10000
    retries = 0

    # Check the video index status until it's processed or max retries reached
    while retries < max_retries:
        # Get the video index status
        index_status_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Index?accessToken={access_token}"
        index_status_response = requests.get(index_status_url)
        index_status = index_status_response.json()

        # If the video has finished indexing, break the loop
        for video in index_status["videos"]:
            if video["state"] == "Processed":
                break
        else:
            # Wait for a while before checking again
            time.sleep(10)  # Wait for 10 seconds
            st.write("the video is processing")
            print("the video is processing")
            retries += 1
            continue
        break

    # If max retries reached, print a message
    if retries == max_retries:
        st.write("Video processing took too long. Please check the video status manually.")
        print("Video processing took too long. Please check the video status manually.")
    else:
        return video_id

@st.cache_data
def insert_speech_general_info(speech_vi_video_id, speech_date, speech_speaker,speech_description):
   
    # Define your server details
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish the connection
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    

    sql = ''' INSERT INTO speech_general_info(speech_vi_video_id, speech_date, speech_speaker,speech_description)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, (speech_vi_video_id, speech_date, speech_speaker,speech_description))
    conn.commit()
    


def main(): 

    api_key = os.getenv('AZURE_OPENAI_KEY')
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish a connection to the database
    conn = pyodbc.connect(odbc_conn_str)

    st.title('Video Uploader')

    languages = {
                "Afrikaans": "af-ZA",
                "Arabic (Israel)": "ar-IL",
                "Arabic (Iraq)": "ar-IQ",
                "Arabic (Jordan)": "ar-JO",
                "Arabic (Kuwait)": "ar-KW",
                "Arabic (Lebanon)": "ar-LB",
                "Arabic (Oman)": "ar-OM",
                "Arabic (Palestinian Authority)": "ar-PS",
                "Arabic (Qatar)": "ar-QA",
                "Arabic (Saudi Arabia)": "ar-SA",
                "Arabic (United Arab Emirates)": "ar-AE",
                "Arabic Egypt": "ar-EG",
                "Catalan": "ca-ES",
                "Czech": "cs-CZ",
                "Welsh": "cy-GB",
                "Danish": "da-DK",
                "German": "de-DE",
                "English": "en-US",
                "Spanish": "es-ES",
                "Basque": "eu-ES",
                "Persian": "fa-IR",
                "Finnish": "fi-FI",
                "Filipino": "fil-PH",
                "French": "fr-FR",
                "Galician": "gl-ES",
                "Gujarati": "gu-IN",
                "Hebrew": "he-IL",
                "Hindi": "hi-IN",
                "Croatian": "hr-HR",
                "Hungarian": "hu-HU",
                "Indonesian": "id-ID",
                "Italian": "it-IT",
                "Japanese": "ja-JP",
                "Kannada": "kn-IN",
                "Korean": "ko-KR",
                "Lithuanian": "lt-LT",
                "Latvian": "lv-LV",
                "Malayalam": "ml-IN",
                "Marathi": "mr-IN",
                "Dutch": "nl-NL",
                "Norwegian Bokmål": "nb-NO",
                "Polish": "pl-PL",
                "Portuguese": "pt-PT",
                "Punjabi": "pa-IN",
                "Romanian": "ro-RO",
                "Russian": "ru-RU",
                "Slovak": "sk-SK",
                "Slovenian": "sl-SI",
                "Swedish": "sv-SE",
                "Tamil": "ta-IN",
                "Telugu": "te-IN",
                "Thai": "th-TH",
                "Turkish": "tr-TR",
                "Ukrainian": "uk-UA",
                "Urdu": "ur-PK",
                "Vietnamese": "vi-VN",
                "Chinese Simplified": "zh-CN",
                "Chinese Traditional": "zh-TW"
                # Add more languages here...
                }
    #youtube_url = st.sidebar.text_input('Enter YouTube URL:', key='youtube_url_1')
    # Create a select box in the sidebar for language selection. The options are the keys of the 'languages' dictionary.
    selected_language = st.sidebar.selectbox("Select a speech language:", list(languages.keys()))
    names = ["Hasan Nasrallah", "Joy Biden", "Mohammed Bin Salman"]
    speech_speaker = st.sidebar.selectbox('Select the speaker a name', names)
    # Generate a list of dates for the select box

    speech_date = st.sidebar.date_input('Select a the speech date')
    # Create a text input field in the sidebar for the speech description
    speech_description = st.sidebar.text_input('Enter speech description:', key='speech_description')
    # Add a radio button for the source of the video
    # Add a radio button for the source of the video
    source = st.radio('Select the source of the video:', ('YouTube', 'Local'))
    speech_vi_video_id = None  # Initialize the variable

    if selected_language: 
        language_code = languages[selected_language]  # Assign a value to language_code here
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi'], key='UploadButton1')

        if uploaded_file is not None:
            # Call the upload_to_video_indexer function with the selected source
            video_id = upload_to_video_indexer_fromlocalfile(uploaded_file, language_code, speech_speaker, speech_description)
            st.write(f'Video ID: {video_id}')
        
        if source == 'YouTube':
            youtube_url = st.text_input('Enter YouTube URL:', key='youtube_url')
            upload_button = st.button('Upload Video', key='UploadButton2')

            if upload_button and youtube_url:
                video_name = download_youtube_video(youtube_url)
                print("the youtube url is before download : "+ youtube_url )
                print("the selected language code: "+ languages[selected_language])
                speech_vi_video_id = upload_to_video_indexer(video_name,language_code,speech_speaker,speech_description)
                if speech_vi_video_id is not None:
                    st.write("Finish to upload the video, the video id is: "+ speech_vi_video_id)
                    insert_speech_general_info(speech_vi_video_id, speech_date, speech_speaker,speech_description)
                else:
                    st.write("Failed to upload the video.")
                




# This is a common Python idiom. It checks if this script is being run directly by the Python interpreter.
if __name__ == "__main__":

    # If the script is being run directly, it calls the main() function.
    main()
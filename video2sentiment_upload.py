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

from sqlalchemy import create_engine




# Import the function from getaccesstoken.py
from getaccesstoken import get_access_token








@st.cache_data
def download_youtube_video(youtube_url):
    # Print the YouTube URL
    print("the youtube url is: "+ youtube_url)
    
    # Initialize video_name variable
    video_name = None

   
    
    # Create a YouTube object with the provided URL
    yt = YouTube(youtube_url)

    # Get the first stream of the video
    video = yt.streams.first()

    # Get the title of the video
    video_name = video.title
    
    # Define the path where the video will be downloaded
    download_path = "/Users/robenhai/video2sentiment/videos"
    
    # Check video name length
    if len(video_name) > 80:
        # Truncate the video name to 80 characters
        video_name = video_name[:80]  
        
        # Remove special characters from video_name
        video_name = re.sub(r'\W+', '', video_name)  
        
        # Add file extension to the video name
        video_name = video_name + ".mp4" 
        
        # Download the video with the specified name to the specified path
        video.download(download_path, filename=video_name) 
        
        # Print the video name and a message indicating the download is complete
        print("the video name is: "+ video_name)
        print("finished downloading the video")
    else:
        # If the video name is not longer than 80 characters, remove special characters
        video_name = re.sub(r'\W+', '', video_name)  
        
        # Add file extension to the video name
        video_name = video_name + ".mp4" 
        
        # Download the video with the specified name to the specified path
        video.download(download_path, filename=video_name) 
        
        # The following print statements are commented out and will not execute
        #print("the video have short name and his name is: "+ video_name)
        #print("finished downloading the video")
    
    # Return the name of the downloaded video
    return video_name

@st.cache_data
def upload_to_video_indexer(video_name,language_code,speech_speaker,description):
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



#     # Initialize the AzureOpenAI client with the API key, API version, and endpoint
#     client = AzureOpenAI(
#         api_key=api_key,  
#         api_version="2024-02-01",
#         azure_endpoint = azure_endpoint,
#         )
        
#     # Define the deployment name. This should match the name you chose when deploying the model.
#     deployment_name='gpt-4o' 

#     # Open the captions file for the given video and read its content
#     # with open(f"{video_name}_captions.txt", "r") as captions_file:
#     #     captions = captions_file.read()

#     # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
#     # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
#     # The user message is the content of the captions file.
#     for _ in range(15):  # Retry up to 5 times
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o", 
#                 messages=[
#                     {"role": "system", "content": "you are a professional psychologist and analyst who deals with analyzing text as data. As part of your work, you deal with extracting entities from a text, as well as extracting the feelings and sentiment towards them as indicated by the text. Please read the text below and per each sentence list all the subjects of the sentence. Make sure to list all the subjects (people, organizations, entities, countries…) of the sentence. Make sure the subject is no more than 3 words. Per each sentence, tag the sentiment towards each subject as a number between -1 and 1 where -1 is Extremely Negative and 1 is Extremely Positive, and 0 is Neutral and the emotions in each sentence above, regarding the entities from the pool of the following emotions: sadness, anger, fear, hate, jealousy, contempt, disappointment, shame, joy, love, trust, pride, compassion, gratitude, hope and surprise. All the results should appear in a table. Whereas the first column name in english of the table the sentence number, the second column should hold the text itself, the third column name in english is the entity, the fourth column name in english is the sentiment and the fifth column name in english is the emotion. Add another column in english for the empathy of the speaker for each sentence, whereas 0 for no empathy and 1 for high empathy. keep the data in the table in the original language , Please do not ignore occurrences of terrorist organizations."},
#                     {"role": "user", "content": speech_caption_hebrew_language}
#                 ],
#                 temperature=0
#             )
#             break  # If the request was successful, break the loop
#         except AzureOpenAI.APIStatusError as e:
#             if 'upstream request timeout' in str(e):
#                 time.sleep(5)  # Wait for 5 seconds before retrying
#             else:
#                 raise  # If it's a different error, raise it

#     # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
#     st.markdown(f"<div style='text-align: right; color: green; font-size: 14px;'>**: ״תוצאת ניתוח הסנטימט בעברית** </div>", unsafe_allow_html=True)
#     # Remove the divider line from the response  
#     response= response.choices[0].message.content
#     #print("the gpt response is:" + response)
#     #response = response.replace("|-----------------|---------------------------------------------------|-----------------|-----------|-------------|---------------|", "")
#     lines = response.split('\n')
#     lines.pop(1)  # remove the second line
#     response = '\n'.join(lines)
#     # Split the response into lines and then split each line by pipe character
#     response = [line.split("|") for line in response.split("\n") if line.strip()]

#     # Remove leading and trailing spaces from each cell
#     response = [[cell.strip() for cell in row] for row in response]

#     # Remove empty strings from the list of columns and data
#     response = [[cell for cell in row if cell] for row in response]

#     # Create a DataFrame
#     df = pd.DataFrame(response[1:], columns=response[0]).reset_index(drop=True)

#     # Display the table in Streamlit
#     st.markdown(df.to_html(index=False), unsafe_allow_html=True)
#     #print(df.columns)
#     return df

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
    
    if selected_language: 

        # Create a text input field in the sidebar for the YouTube URL
        youtube_url = st.sidebar.text_input('Enter YouTube URL:', key='youtube_url_2')

        # Check if a YouTube URL has been entered
        if youtube_url:

            # Print the entered YouTube URL
            print("the youtube url is before download : "+ youtube_url )

            # Download the YouTube video and get the video name
            video_name=download_youtube_video(youtube_url)

            # Print the selected language code
            print("the selected language code: "+ languages[selected_language])

            # Get the language code for the selected language
            language_code=languages[selected_language]

            # Upload the downloaded video to Video Indexer with the selected language code
    #description = quote(video_name)
            speech_vi_video_id = upload_to_video_indexer(video_name,language_code,speech_speaker,speech_description)
            st.write("Finish to upload the video, the video id is: "+ speech_vi_video_id)
            # speech_caption_original_language = download_video_captions_original_language(video_name,speech_vi_video_id,language_code)


            #update generl info table:
            insert_speech_general_info(speech_vi_video_id, speech_date, speech_speaker,speech_description)
            




# This is a common Python idiom. It checks if this script is being run directly by the Python interpreter.
if __name__ == "__main__":

    # If the script is being run directly, it calls the main() function.
    main()
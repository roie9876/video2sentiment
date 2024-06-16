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
def upload_to_video_indexer(video_name,language_code):
    # Fetch environment variables
    print("start the upload VI process")
    subscription_key = os.getenv('SUBSCRIPTION_KEY')
    location = os.getenv('LOCATION')
    account_id = os.getenv('ACCOUNT_ID')
    api_url = os.getenv('API_URL')
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    download_path = os.getenv('DOWNLOAD_PATH')
    
    # Get access token
    description = quote(video_name)
    print ("the video name is: "+ video_name)
    access_token = get_access_token()
    print("the access token is: "+ access_token)


     # Free text to be displayed in the Streamlit UI
    original_text = '<p style="color:red;font-weight:bold;">This is original text from video.</p>'  
    # Construct the upload URL
    upload_url = f"{api_url}/{location}/Accounts/{account_id}/Videos?accessToken={access_token}&name={video_name}&description={description}&language={language_code}"

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
    max_retries = 120
    retries = 0

    # Check the video index status until it's processed or max retries reached
    while retries < max_retries:
        # Get the video index status
        index_status_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Index?accessToken={access_token}"
        index_status_response = requests.get(index_status_url)
        index_status = index_status_response.json()

        # If the video has finished indexing, break the loop
        if index_status["state"] == "Processed":
            break

        # Wait for a while before checking again
        time.sleep(10)  # Wait for 10 seconds
        retries += 1

    # If max retries reached, print a message
    if retries == max_retries:
        print("Video processing took too long. Please check the video status manually.")
    else:
        # Get the captions for the video
        captions_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Captions?accessToken={access_token}&format=txt&language=he"
        captions_response = requests.get(captions_url)

        # Write the captions to a text file
        response_content = captions_response.content
        with open(f"{video_name}_captions.txt", "wb") as captions_file:
            captions_file.write(response_content)

        # Read the file and print to Streamlit UI
        with open(f"{video_name}_captions.txt", "r") as captions_file:
            captions = captions_file.read()
        st.markdown(f"<div style='color: blue; font-size: 14px; text-align: right;'>{original_text}<br/>{captions}</div>", unsafe_allow_html=True)



@st.cache_data
def openai_summery(video_name):   
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key="e47071ca963e411f8f9f074e053fc875",  
        api_version="2024-02-01",
        azure_endpoint = "https://openairoie.openai.azure.com/"
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 

    # Open the captions file for the given video and read its content
    with open(f"{video_name}_captions.txt", "r") as captions_file:
        captions = captions_file.read()

    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "עליך לבנות תקציר של הנאום עם התייחסות לנקודות מרכזיות "},
            {"role": "user", "content": captions}
        ],
        temperature=0
    )
    
    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    st.markdown(f"<div style='text-align: right; color: red; font-size: 14px;'>**:תקציר הנאום** {response.choices[0].message.content}</div>", unsafe_allow_html=True)

@st.cache_data
def openai_sentiment(video_name):   
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key="e47071ca963e411f8f9f074e053fc875",  
        api_version="2024-02-01",
        azure_endpoint = "https://openairoie.openai.azure.com/"
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 

    # Open the captions file for the given video and read its content
    with open(f"{video_name}_captions.txt", "r") as captions_file:
        captions = captions_file.read()

    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "תבצע חלוקה של הנאום לפסקאות ועבור כל פסקה לנתח את  הסטימנט רגשי חיובי, שלילי, שמחה, קנאה, ועוד רגשות"},
            {"role": "user", "content": captions}
        ],
        temperature=0
    )
    
    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    st.markdown(f"<div style='text-align: right; color: green; font-size: 14px;'>**:״תוצאת ניתוח הסנטימט** {response.choices[0].message.content}</div>", unsafe_allow_html=True)



def main():
    #print("this is the main function")
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
    selected_language = st.sidebar.selectbox("Select a language:", list(languages.keys()))

    # Check if a language has been selected
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
            upload_to_video_indexer(video_name,language_code)

            # Print a message before calling the OpenAI sentiment analysis function
            print("before openai_sentiment")

            # Call the OpenAI sentiment analysis function on the downloaded video
            openai_summery(video_name)
            
            print("before openai_summery")
            openai_sentiment(video_name)




# This is a common Python idiom. It checks if this script is being run directly by the Python interpreter.
if __name__ == "__main__":

    # If the script is being run directly, it calls the main() function.
    main()
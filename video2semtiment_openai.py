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
from SessionState import get as SessionState
# Importing necessary modules from VideoIndexerClient
from VideoIndexerClient.Consts import Consts
from VideoIndexerClient.VideoIndexerClient import VideoIndexerClient
from streamlit_ace import st_ace
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

# Function to plot pie chart
def plot_pie_chart(df, min_occurrences=0):
    # Group by 'speech_entity' and 'speech_emotion' and count the number of occurrences
    df_grouped = df.groupby(['speech_entity', 'speech_emotion'])
    
    # Filter groups with more than min_occurrences
    df_grouped = df_grouped.filter(lambda x: len(x) >= min_occurrences).groupby(['speech_entity', 'speech_emotion']).size().reset_index(name='count')

    # Creating the pie chart
    fig = px.pie(df_grouped, values='count', names='speech_entity', color='speech_emotion',
                 color_discrete_sequence=px.colors.sequential.Rainbow)
    return fig



# Function to get speech sentiment in original language
def get_speech_sentiment_original_language(video_id):
    # Defining the SQL query
    query = """
    SELECT speech_sentence_number, speech_text_original_language, speech_entity, speech_sentiment, speech_emotion, speech_empathy_level
    FROM speech_sentiment_original_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df

# Function to get speech sentiment in Hebrew language
def get_speech_sentiment_hebrew_language(video_id):
    # Defining the SQL query
    query = """
    SELECT speech_sentence_number, speech_text_original_language, speech_entity, speech_sentiment, speech_emotion, speech_empathy_level
    FROM speech_sentiment_hebrew_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df

# Function to get speech caption summary in original language
def speech_caption_summary_original_language(video_id):
    # Defining the SQL query
    query = """
    SELECT speech_caption_original_language
    FROM speech_general_original_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df

# Function to get speech caption in original language
def speech_caption_original_language(video_id):
    # Defining the SQL query
    query = """
    SELECT speech_caption_summary_original_language 
    FROM speech_general_original_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df

# Function to get speech caption in Hebrew language
def speech_caption_hebrew_language(video_id):
    # Defining the SQL query
    query = """
    SELECT 	speech_caption_hebrew_language 
    FROM speech_general_hebrew_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df

# Function to get speech caption summary in Hebrew language
def speech_caption_summary_hebrew_language(video_id):
    # Defining the SQL query
    query = """
    SELECT 	speech_caption_summary_hebrew_language 
    FROM speech_general_hebrew_language 
    WHERE speech_vi_video_id = ?
    """

    # Executing the query and converting the result into a DataFrame
    df = pd.read_sql_query(query, conn, params=[video_id])

    # Returning the DataFrame
    return df



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




def download_video_captions_original_language(video_id):
    
        # Get the captions for the video
        # Fetch environment variables
        print("start download captions process")
        subscription_key = os.getenv('SUBSCRIPTION_KEY')
        location = os.getenv('LOCATION')
        account_id = os.getenv('ACCOUNT_ID')
        api_url = os.getenv('API_URL')
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        download_path = os.getenv('DOWNLOAD_PATH')
        access_token = get_access_token()
        captions_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Captions?accessToken={access_token}&format=txt"
        captions_response = requests.get(captions_url)
        original_text = '<p style="color:red;font-weight:bold;">הנאום המלא בשפת המקור.</p>' 
        # Write the captions to a text file
        response_content = captions_response.content
        #with open(f"{video_name}_captions.txt", "wb") as captions_file:
        #    captions_file.write(response_content)

        # Read the file and print to Streamlit UI
        #with open(f"{video_name}_captions.txt", "r") as captions_file:
        #    captions = captions_file.read()
        response_content = response_content.decode('utf-8')
        st.markdown(f"<div style='color: blue; font-size: 14px; text-align: right;'>{original_text}<br/>{response_content}</div>", unsafe_allow_html=True)
        
        return response_content

@st.cache_data
def download_video_captions_hebrew_language(video_id):
    
        # Get the captions for the video
        # Fetch environment variables
        print("start download captions process")
        subscription_key = os.getenv('SUBSCRIPTION_KEY')
        location = os.getenv('LOCATION')
        account_id = os.getenv('ACCOUNT_ID')
        api_url = os.getenv('API_URL')
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        download_path = os.getenv('DOWNLOAD_PATH')
        access_token = get_access_token()
        captions_url = f"{api_url}/{location}/Accounts/{account_id}/Videos/{video_id}/Captions?accessToken={access_token}&format=txt&language=he-IL"
        captions_response = requests.get(captions_url)
        original_text = '<p style="color:red;font-weight:bold;">הנאום במלא מתורגם לעברית.</p>' 
        # Write the captions to a text file
        response_content = captions_response.content
        #with open(f"{video_name}_captions.txt", "wb") as captions_file:
        #    captions_file.write(response_content)

        # Read the file and print to Streamlit UI
        #with open(f"{video_name}_captions.txt", "r") as captions_file:
        #    captions = captions_file.read()
        response_hebrew_content = response_content.decode('utf-8')
        st.markdown(f"<div style='color: blue; font-size: 14px; text-align: right;'>{original_text}<br/>{response_hebrew_content}</div>", unsafe_allow_html=True)
        
        return response_hebrew_content


@st.cache_data
def openai_summery(api_key,azure_endpoint,speech_caption_original_language):   
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key=api_key,  
        api_version="2024-02-01",
        azure_endpoint = azure_endpoint,
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 

    # Open the captions file for the given video and read its content
    # with open(f"{video_name}_captions.txt", "r") as captions_file:
    #     captions = captions_file.read()

    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "you need to do summery of the speech with the main points in the speech language"},
            {"role": "user", "content": speech_caption_original_language}
        ],
        temperature=0
    )
    
    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    st.markdown(f"<div style='text-align: right; color: red; font-size: 14px;'>**: תקציר הנאום בשפת המקור** {response.choices[0].message.content}</div>", unsafe_allow_html=True)
    return response.choices[0].message.content

@st.cache_data
def openai_hebrew_summery(api_key,azure_endpoint,speech_caption_hebrew_language):  
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key=api_key,  
        api_version="2024-02-01",
        azure_endpoint = azure_endpoint,
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 
    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "עליך לבנות תקציר של הנאום עם התייחסות לנקודות מרכזיות "},
            {"role": "user", "content": speech_caption_hebrew_language}
        ],
        temperature=0
    )
    
    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    st.markdown(f"<div style='text-align: right; color: red; font-size: 14px;'>**:תקציר הנאום** {response.choices[0].message.content}</div>", unsafe_allow_html=True)
    return response.choices[0].message.content

@st.cache_data
def openai_sentiment(api_key,azure_endpoint,speech_caption_original_language):   
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key=api_key,  
        api_version="2024-02-01",
        azure_endpoint = azure_endpoint,
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 

    # Open the captions file for the given video and read its content
    # with open(f"{video_name}_captions.txt", "r") as captions_file:
    #     captions = captions_file.read()

    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    for _ in range(15):  # Retry up to 5 times
        try:
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "you are a professional psychologist and analyst who deals with analyzing text as data. As part of your work, you deal with extracting entities from a text, as well as extracting the feelings and sentiment towards them as indicated by the text. Please read the text below and per each sentence list all the subjects of the sentence. Make sure to list all the subjects (people, organizations, entities, countries…) of the sentence. Make sure the subject is no more than 3 words. Per each sentence, tag the sentiment towards each subject as a number between -1 and 1 where -1 is Extremely Negative and 1 is Extremely Positive, and 0 is Neutral and the emotions in each sentence above, regarding the entities from the pool of the following emotions: sadness, anger, fear, hate, jealousy, contempt, disappointment, shame, joy, love, trust, pride, compassion, gratitude, hope and surprise. All the results should appear in a table. Whereas the first column name in english of the table the sentence number, the second column should hold the text itself, the third column name in english is the entity, the fourth column name in english is the sentiment and the fifth column name in english is the emotion. Add another column in english for the empathy of the speaker for each sentence, whereas 0 for no empathy and 1 for high empathy. keep the data in the table in the original language , Please do not ignore occurrences of terrorist organizations. dont add information like this in the end of your response:This table captures the entities, sentiments, emotions, and empathy levels for each sentence in the provided text."},
                    {"role": "user", "content": speech_caption_original_language}
                ],
                temperature=0
            )
            break  # If the request was successful, break the loop
        except AzureOpenAI.APIStatusError as e:
            if 'upstream request timeout' in str(e):
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                raise  # If it's a different error, raise it

    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    #st.markdown(f"<div style='text-align: right; color: green; font-size: 14px;'>**:״תוצאת ניתוח הסנטימט** </div>", unsafe_allow_html=True)
    # Remove the divider line from the response  
    response= response.choices[0].message.content
    #print("the gpt response is:" + response)
    #response = response.replace("|-----------------|---------------------------------------------------|-----------------|-----------|-------------|---------------|", "")
    lines = response.split('\n')
    lines.pop(1)  # remove the second line
    response = '\n'.join(lines)
    # Split the response into lines and then split each line by pipe character
    response = [line.split("|") for line in response.split("\n") if line.strip()]

    # Remove leading and trailing spaces from each cell
    response = [[cell.strip() for cell in row] for row in response]

    # Remove empty strings from the list of columns and data
    response = [[cell for cell in row if cell] for row in response]

    # Create a DataFrame
    df = pd.DataFrame(response[1:], columns=response[0]).reset_index(drop=True)

    # Display the table in Streamlit
    #st.markdown(df.to_html(index=False), unsafe_allow_html=True)
    #print(df.columns)
    return df


@st.cache_data
def openai_hebrew_sentiment(api_key,azure_endpoint,speech_caption_hebrew_language):   
    # Initialize the AzureOpenAI client with the API key, API version, and endpoint
    client = AzureOpenAI(
        api_key=api_key,  
        api_version="2024-02-01",
        azure_endpoint = azure_endpoint,
        )
        
    # Define the deployment name. This should match the name you chose when deploying the model.
    deployment_name='gpt-4o' 

    # Open the captions file for the given video and read its content
    # with open(f"{video_name}_captions.txt", "r") as captions_file:
    #     captions = captions_file.read()

    # Create a chat completion with the OpenAI API. The chat consists of a system message and a user message.
    # The system message instructs the model to analyze the sentiment and emotions of each paragraph in the speech.
    # The user message is the content of the captions file.
    for _ in range(15):  # Retry up to 5 times
        try:
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "you are a professional psychologist and analyst who deals with analyzing text as data. As part of your work, you deal with extracting entities from a text, as well as extracting the feelings and sentiment towards them as indicated by the text. Please read the text below and per each sentence list all the subjects of the sentence. Make sure to list all the subjects (people, organizations, entities, countries…) of the sentence. Make sure the subject is no more than 3 words. Per each sentence, Given a transcript of a speech, identify the entities or groups referred to by the pronouns they, us, and other similar pronouns. Use the context of the speech to infer who or what these pronouns are referring to, us with tag the sentiment towards each subject as a number between -1 and 1 where -1 is Extremely Negative and 1 is Extremely Positive, and 0 is Neutral and the emotions in each sentence above, regarding the entities from the pool of the following emotions: sadness, anger, fear, hate, jealousy, contempt, disappointment, shame, joy, love, trust, pride, compassion, gratitude, hope and surprise. All the results should appear in a table. Whereas the first column must name in english of the table the sentence number, the second column should hold the text itself, the third column name in english is the entity, the fourth column name in english is the sentiment and the fifth column name in english is the emotion. Add another column in english for the empathy of the speaker for each sentence, whereas 0 for no empathy and 1 for high empathy. keep the data from raw 2  in the table in the original language , Please do not ignore occurrences of terrorist organizations."},
                    {"role": "user", "content": speech_caption_hebrew_language}
                ],
                temperature=0
            )
            break  # If the request was successful, break the loop
        except AzureOpenAI.APIStatusError as e:
            if 'upstream request timeout' in str(e):
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                raise  # If it's a different error, raise it

    # Display the sentiment analysis result in the Streamlit app. The result is displayed in red text, aligned to the right.
    #st.markdown(f"<div style='text-align: right; color: green; font-size: 14px;'>**: ״תוצאת ניתוח הסנטימט בעברית** </div>", unsafe_allow_html=True)
    # Remove the divider line from the response  
    response= response.choices[0].message.content
    #print("the gpt response is:" + response)
    #response = response.replace("|-----------------|---------------------------------------------------|-----------------|-----------|-------------|---------------|", "")
    lines = response.split('\n')
    lines.pop(1)  # remove the second line
    response = '\n'.join(lines)
    # Split the response into lines and then split each line by pipe character
    response = [line.split("|") for line in response.split("\n") if line.strip()]

    # Remove leading and trailing spaces from each cell
    response = [[cell.strip() for cell in row] for row in response]

    # Remove empty strings from the list of columns and data
    response = [[cell for cell in row if cell] for row in response]

    # Create a DataFrame
    df = pd.DataFrame(response[1:], columns=response[0]).reset_index(drop=True)

    # Display the table in Streamlit
    #st.markdown(df.to_html(index=False), unsafe_allow_html=True)
    #print(df.columns)
    return df

@st.cache_data
def insert_speech_general_original_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_original_language,speech_caption_summary_original_language):
    

    # Define your server details
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish the connection
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()

    #delete all old data where for the existing video id
    cur = conn.cursor()
    sql = ''' DELETE FROM speech_general_original_language WHERE speech_vi_video_id = ? '''
    cur.execute(sql, (speech_vi_video_id,))     

    sql = ''' INSERT INTO speech_general_original_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_original_language,speech_caption_summary_original_language)
              VALUES(?,?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, (speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_original_language,speech_caption_summary_original_language))
    conn.commit()
    
@st.cache_data
def insert_speech_general_hebrew_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_hebrew_language,speech_caption_summary_hebrew_language):
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish the connection
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    cur = conn.cursor()
    #delete all old data where for the existing video id
    sql = ''' DELETE FROM speech_general_hebrew_language WHERE speech_vi_video_id = ? '''
    cur.execute(sql, (speech_vi_video_id,))

    sql = ''' INSERT INTO speech_general_hebrew_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_hebrew_language,speech_caption_summary_hebrew_language)
              VALUES(?,?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, (speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_hebrew_language,speech_caption_summary_hebrew_language))
    conn.commit()

@st.cache_data
def insert_speech_general_hebrew_language_with_sentiment(speech_vi_video_id, hebrew_sentiment_result):
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish the connection
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()
    cur = conn.cursor()
    #delete all old data where for the existing video id
    sql = ''' DELETE FROM speech_sentiment_hebrew_language WHERE speech_vi_video_id = ? '''
    cur.execute(sql, (speech_vi_video_id,))   

    # Convert the list of dictionaries to a DataFrame
    hebrew_sentiment_result = pd.DataFrame(hebrew_sentiment_result)

    # Modify the DataFrame
    hebrew_sentiment_result = hebrew_sentiment_result.drop(hebrew_sentiment_result.index[0])
    hebrew_sentiment_result['speech_vi_video_id'] = speech_vi_video_id
    hebrew_sentiment_result.columns = hebrew_sentiment_result.columns.str.replace(' ', '_')

    # Rename the columns to match the database table
    hebrew_sentiment_result = hebrew_sentiment_result.rename(columns={
        'Sentence_Number': 'speech_sentence_number',
        'Text': 'speech_text_original_language',
        'Entity': 'speech_entity',
        'Sentiment': 'speech_sentiment',
        'Emotion': 'speech_emotion',
        'Empathy': 'speech_empathy_level'
    })

    # Write the DataFrame to a SQL database
    for index, row in hebrew_sentiment_result.iterrows():
        cursor.execute("""
            INSERT INTO speech_sentiment_hebrew_language (speech_sentence_number, speech_text_original_language, speech_entity, speech_sentiment, speech_emotion, speech_empathy_level, speech_vi_video_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, row['speech_sentence_number'], row['speech_text_original_language'], row['speech_entity'], row['speech_sentiment'], row['speech_emotion'], row['speech_empathy_level'], row['speech_vi_video_id'])
    conn.commit()



    

@st.cache_data
def insert_speech_general_original_language_with_sentiment(speech_vi_video_id, sentiment_result):
    odbc_conn_str = os.getenv('ODBC_CONN_STR')

    # Establish the connection
    conn = pyodbc.connect(odbc_conn_str)
    cursor = conn.cursor()

    # Delete all old data where for the existing video id
    cur = conn.cursor()
    sql = ''' DELETE FROM speech_sentiment_original_language WHERE speech_vi_video_id = ? '''
    cur.execute(sql, (speech_vi_video_id,))  

    # Convert the list of dictionaries to a DataFrame
    sentiment_result = pd.DataFrame(sentiment_result)

    # Modify the DataFrame
    sentiment_result = sentiment_result.drop(sentiment_result.index[0])
    sentiment_result['speech_vi_video_id'] = speech_vi_video_id
    sentiment_result.columns = sentiment_result.columns.str.replace(' ', '_')

    # Rename the columns to match the database table
    sentiment_result = sentiment_result.rename(columns={
        'Sentence_Number': 'speech_sentence_number',
        'Text': 'speech_text_original_language',
        'Entity': 'speech_entity',
        'Sentiment': 'speech_sentiment',
        'Emotion': 'speech_emotion',
        'Empathy': 'speech_empathy_level'
    })

    # Write the DataFrame to a SQL database
    for index, row in sentiment_result.iterrows():
        cursor.execute("""
            INSERT INTO speech_sentiment_original_language (speech_sentence_number, speech_text_original_language, speech_entity, speech_sentiment, speech_emotion, speech_empathy_level, speech_vi_video_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, row['speech_sentence_number'], row['speech_text_original_language'], row['speech_entity'], row['speech_sentiment'], row['speech_emotion'], row['speech_empathy_level'], row['speech_vi_video_id'])
    conn.commit()


def fetch_speech_general_info(video_id):
    #print(f"Video ID: {video_id}")  # Debug Step 1 & 2
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT speech_date, speech_speaker, speech_description FROM speech_general_info WHERE speech_vi_video_id = ?", (str(video_id),))
    except Exception as e:
        print(f"Database error: {e}")  # Debug Step 4
    row = cursor.fetchone()
    #print(f"Query Result: {row}")  # Debug Step 3
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
            # Store the video_id in the ace input field
            #st_ace(value=video_id, key="video_id")
            #st.write("working on video_id:" + video_id)
            speech_vi_video_id=video_id
            #st.write("working on video_id:" + speech_vi_video_id)
                # Fetch speech data
            speech_data = fetch_speech_general_info(speech_vi_video_id)
            # Convert speech_data to a DataFrame
            #df = pd.DataFrame(speech_data, columns=['Column1', 'Column2', 'Column3'])

            # Display the DataFrame as a table in Streamlit
            #st.table(df)
            
            if speech_data is not None:
                speech_date = speech_data['date']
                speech_speaker = speech_data['speaker']
                speech_description = speech_data['description']
                
            
                speech_vi_video_id = video_id


                speech_caption_original_language = download_video_captions_original_language(speech_vi_video_id)
                st.write("Speech original lanuage" + speech_caption_original_language)

                # # Call the OpenAI sentiment analysis function on the downloaded video
                speech_caption_summary_original_language = openai_summery(api_key,azure_endpoint,speech_caption_original_language)
                #st.write("Speech summary for the original lanuage"+speech_caption_summary_original_language)

                insert_speech_general_original_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_original_language,speech_caption_summary_original_language)
                
                sentiment_result = openai_sentiment(api_key,azure_endpoint,speech_caption_original_language)
                #st.write("the sentiment analysis of the original language:" + sentiment_result)
                
                # Split the text into chunks of 500 words
                original_words = speech_caption_original_language.split()
                original_chunks = [' '.join(original_words[i:i + 500]) for i in range(0, len(original_words), 500)]

                # Initialize an empty dataframe to store the results
                original_merged_results = pd.DataFrame()

                # For each chunk, call the openai_sentiment function and append the result to the dataframe
                for chunk in original_chunks:
                    result = openai_sentiment(api_key, azure_endpoint, chunk)
                    result_df = pd.DataFrame(result)  # Assuming result is a list of dictionaries

                    original_merged_results = pd.concat([original_merged_results, result_df], ignore_index=True)

                # Overwrite 'Sentence Number' with the index + 1 (since index starts at 0)
                original_merged_results['Sentence Number'] = original_merged_results.index + 1

                # Convert the DataFrame to a markdown table and display it
                st.markdown("The sentiment analysis of the original language:")
                st.markdown(original_merged_results.to_markdown(index=False))

                # Convert the DataFrame to a list of dictionaries without the index and pass it to the function
                sentiment_result = original_merged_results.to_dict('records')
                insert_speech_general_original_language_with_sentiment(speech_vi_video_id, sentiment_result)

                
                

                # #take care of hebrew language        
                speech_caption_hebrew_language = download_video_captions_hebrew_language(speech_vi_video_id)
                #st.write("Speech hebrew lanuage" + speech_caption_hebrew_language)

                speech_caption_summary_hebrew_language = openai_hebrew_summery(api_key,azure_endpoint,speech_caption_hebrew_language)
                #st.write("Speech summary for the hebrew lanuage" + speech_caption_summary_hebrew_language)

                insert_speech_general_hebrew_language(speech_vi_video_id, speech_date, speech_speaker,speech_description,speech_caption_hebrew_language,speech_caption_summary_hebrew_language)                 
                
                
                hebrew_sentiment_result = openai_hebrew_sentiment(api_key,azure_endpoint,speech_caption_hebrew_language)
                #st.write("the sentiment analysis of the hebrew language:" + sentiment_result)
                # Split the text into chunks of 1000 words
                hebrew_words = speech_caption_hebrew_language.split()
                hebrew_chunks = [' '.join(hebrew_words[i:i + 500]) for i in range(0, len(hebrew_words), 500)]

                # Initialize an empty dataframe to store the results
                hebrew_merged_results = pd.DataFrame()

                # For each chunk, call the openai_hebrew_sentiment function and append the result to the dataframe
                for chunk in hebrew_chunks:
                    #st.write("working on chunk:" + chunk)
                    result = openai_hebrew_sentiment(api_key, azure_endpoint, chunk)
                    result_df = pd.DataFrame(result)  # Assuming result is a list of dictionaries

                    hebrew_merged_results = pd.concat([hebrew_merged_results, result_df], ignore_index=True)

                # Overwrite 'Sentence Number' with the index + 1 (since index starts at 0)
                hebrew_merged_results['Sentence Number'] = hebrew_merged_results.index + 1

                # Convert the DataFrame to a markdown table and display it
                st.markdown("The sentiment analysis of the Hebrew language:")
                st.markdown(hebrew_merged_results.to_markdown(index=False))
                # Convert the DataFrame to a list of dictionaries without the index and pass it to the function
                hebrew_sentiment_result = hebrew_merged_results.to_dict('records')
                insert_speech_general_hebrew_language_with_sentiment(speech_vi_video_id, hebrew_sentiment_result)




                

  
# Ensure the main function is called only when the script is executed directly  
if __name__ == "__main__":  
    main()  
# Importing necessary libraries
import streamlit as st
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
import concurrent.futures
from pprint import pprint
from streamlit_ace import st_ace

# Importing necessary modules from VideoIndexerClient
from VideoIndexerClient.Consts import Consts
from VideoIndexerClient.VideoIndexerClient import VideoIndexerClient

# Setting the page layout to wide
st.set_page_config(layout="wide")  

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



# Function to plot pie chart
def plot_pie_chart(df, min_occurrences=1):
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

# Function to fetch speech data
def fetch_speech_data(video_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM speech WHERE speech_vi_video_id = ?", str(video_id))
    rows = cursor.fetchall()
    return rows

# Main function
def main():  
    video_ids = get_all_video_ids()  
    names = ["Hasan Nasrallah", "Joy Biden", "Mohammed Bin Salman"]  
    selected_name = st.sidebar.selectbox('Select a name', names)  
    filtered_videos = [video for video in video_ids['results'] if video.get('metadata') == selected_name] 

    image_button_clicked, video_id = get_all_thumbnail_ids(filtered_videos)

    if image_button_clicked:
        if video_id is not None and video_id != '':
            # Store the video_id in the ace input field
            #st_ace(value="", key="video_id")
        
          
            # Create three columns with more balanced widths  
            col1, col2 = st.columns([1, 2])  
            
            with col1:  

                # original language Display the speech data using Streamlit's text_area for better formatting  
                # Plot the pie chart


                speech_sentiment_hebrew_language = get_speech_sentiment_hebrew_language(video_id)
                speech_caption_summary_hebrew = speech_caption_summary_hebrew_language(video_id)
                fig = plot_pie_chart(speech_sentiment_hebrew_language)
                st.plotly_chart(fig)

                speech_hebrew_language = speech_caption_hebrew_language(video_id)  
                st.text_area("Speech hebrew Language", speech_hebrew_language.to_string(index=False), height=200)  
                st.text_area("Speech Caption Summary hebrew Language", speech_caption_summary_hebrew.to_string(index=False), height=200)            
                st.write(speech_sentiment_hebrew_language)


                speech_sentiment_original_language = get_speech_sentiment_original_language(video_id)
                speech_caption_summary_original = speech_caption_summary_original_language(video_id)

                fig = plot_pie_chart(speech_sentiment_original_language)
                st.plotly_chart(fig)
    
                speech_original_language = speech_caption_original_language(video_id)  
                st.text_area("Speech Original Language", speech_original_language.to_string(index=False), height=200)  
                st.text_area("Speech Caption Summary Original Language", speech_caption_summary_original.to_string(index=False), height=200)            
                st.write(speech_sentiment_original_language)
    

    
    
            with col2:  
                # Display the insights and player widgets with appropriate sizing  
                insights_widget_url = client.get_insights_widgets_url_async(video_id, widget_type='Keywords')  
                st.components.v1.iframe(insights_widget_url, height=520, scrolling=True)  
                
                player_widget_url = client.get_player_widget_url_async(video_id)  
                st.components.v1.iframe(player_widget_url, height=520, scrolling=True)  
                

          

  
# Ensure the main function is called only when the script is executed directly  
if __name__ == "__main__":  
    main()  
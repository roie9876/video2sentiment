# video2sentiment

`video2sentiment` is a Python application that performs sentiment analysis on video content. It uses OpenAI's GPT-4o model and Microsoft's Azure Video Indexer to extract and analyze the sentiment of the speech in the video.

## Features

- Extracts speech from video files using Azure Video Indexer.
- Performs sentiment analysis on the extracted speech using OpenAI's GPT-4o model.
- Stores the sentiment analysis results in a SQL database.
- Supports both original and Hebrew language sentiment analysis.

## Setup

### Prerequisites

- Python 3.7+
- An Azure account with Video Indexer and a SQL database set up.
- An OpenAI API key.

### Installation

1. Clone the repository.
2. Install the required Python packages using pip:

```bash
pip install -r requirements.txt



First, you need to set up your environment variables. 
Your .env file should look like this, with all sensitive information replaced by placeholders:

AccountName='your-account-name'
ResourceGroup='your-resource-group'
SubscriptionId='your-subscription-id'
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP_NAME="your-resource-group-name"
ACCOUNT_NAME="your-account-name"
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
TENANT_ID="your-tenant-id"
API_URL="https://api.videoindexer.ai"
SUBSCRIPTION_KEY="your-subscription-key"
LOCATION="your-location"
ACCOUNT_ID="your-account-id"
DOWNLOAD_PATH="/path/to/your/download/directory"
AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint/"
AZURE_OPENAI_KEY="your-openai-key"
ODBC_CONN_STR='Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-database-server,1433;Database=your-database;Uid=your-username;Pwd={your-password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


Make sure you have Streamlit installed in your Python environment. If not, you can install it using pip:

pip install -r requirments.txt

Finally, you can run your Streamlit application with the following command:
streamlit run video2sent_main.py

This command starts the Streamlit server and opens your default web browser to the app. 
The app will update in real-time as you modify your script.
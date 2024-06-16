import requests
import os

def get_access_token():
    # Define your Azure Video Indexer account details
    subscription_id = os.getenv('SUBSCRIPTION_ID')
    resource_group_name = os.getenv('RESOURCE_GROUP_NAME')
    account_name = os.getenv('ACCOUNT_NAME')

    # Define your Azure credentials
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    tenant_id = os.getenv('TENANT_ID')

    # Define the Azure endpoints
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    token_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.VideoIndexer/accounts/{account_name}/generateAccessToken?api-version=2024-01-01"
    # Get the AAD token
    aad_token_response = requests.post(
        auth_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": "https://management.azure.com/"
        }
    )
    aad_token = aad_token_response.json()["access_token"]

    # Get the Video Indexer token
    vi_token_response = requests.post(
        token_url,
        headers={
            "Authorization": f"Bearer {aad_token}"
        },
        json={
            "permissionType": "Contributor",
            "scope": "Account"
        }
    )

    # Check if the request was successful
    if vi_token_response.status_code == 200:
        response_json = vi_token_response.json()

        # Check if 'accessToken' is in the response
        if 'accessToken' in response_json:
            vi_token = response_json["accessToken"]
            #print("Access token retrieved successfully")
            return vi_token
        else:
            print("'accessToken' not found in the response")
            return None
    else:
        print(f"Request failed with status code: {vi_token_response.status_code}")
        return None
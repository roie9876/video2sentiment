import requests
import os
from azure.identity import DefaultAzureCredential

from VideoIndexerClient.Consts import Consts

tenant_id = os.getenv('TENANT_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_arm_access_token():
    aad_token_response = requests.post(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": "https://management.azure.com/"
        }
    )

    response_json = aad_token_response.json()

    if 'access_token' in response_json:
        aad_token = response_json["access_token"]
        print("the aad token "+aad_token)
        return aad_token
    else:
        print("access_token not found in the response. Response:", response_json)
        return None

# def get_arm_access_token(consts:Consts) -> str:
#     '''
#     Get an access token for the Azure Resource Manager
#     Make sure you're logged in with `az` first

#     :param consts: Consts object
#     :return: Access token for the Azure Resource Manager
#     '''
#     credential = DefaultAzureCredential()
#     scope = f"{consts.AzureResourceManager}/.default" 
#     token = credential.get_token(scope)
#     return token.token


def get_account_access_token_async(consts, arm_access_token, permission_type='Contributor', scope='Account',
                                   video_id=None):
    '''
    Get an access token for the Video Indexer account
    
    :param consts: Consts object
    :param arm_access_token: Access token for the Azure Resource Manager
    :param permission_type: Permission type for the access token
    :param scope: Scope for the access token
    :param video_id: Video ID for the access token, if scope is Video. Otherwise, not required
    :return: Access token for the Video Indexer account
    '''

    headers = {
        'Authorization': 'Bearer ' + arm_access_token,
        'Content-Type': 'application/json'
    }

    url = f'{consts.AzureResourceManager}/subscriptions/{consts.SubscriptionId}/resourceGroups/{consts.ResourceGroup}' + \
          f'/providers/Microsoft.VideoIndexer/accounts/{consts.AccountName}/generateAccessToken?api-version={consts.ApiVersion}'

    params = {
        'permissionType': permission_type,
        'scope': scope
    }
    
    if video_id is not None:
        params['videoId'] = video_id

    response = requests.post(url, json=params, headers=headers)
    
    # check if the response is valid
    response.raise_for_status()
    
    access_token = response.json().get('accessToken')

    return access_token
import os
from lib.api360 import API360

def get_service_app_token(email: str) -> str:
    response = API360.get_service_app_token(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        subject_token=email,
        subject_token_type='urn:yandex:params:oauth:token-type:email'
    )
    if 'error' in response:
        raise Exception(f'{response["error"]}: {response["error_description"]}')

    return(response['access_token'])
    
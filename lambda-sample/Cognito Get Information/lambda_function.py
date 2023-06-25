import boto3
import hashlib
import hmac
import base64

client_id = '2q727e3f0okdgje4euk6uvqf04'
client_secret = 'vtrv2vat7j0mbob73dkdv171gtmp47fhrpnbp3k388uufkkuuah'
region_name = 'ap-northeast-2'

def lambda_handler(event, context):
    if "authorizationToken" in event:
        auth_info = event['authorizationToken']
        username, password = auth_info.split(',')
        
        result = check_authentication(username, password)
        
        if result is True:
            return generate_policy('user_id', 'Allow', event['methodArn'])
        else:
            return generate_policy('user_id', 'Deny', event['methodArn'])
    else:
        name = event['name']
        return check_api_name(name)
        
def generate_policy(principal_id, effect, resource):
    policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'execute-api:Invoke',
            'Effect': effect,
            'Resource': resource
        }]
    }
    
    auth_response = {
        'principalId': principal_id,
        'policyDocument': policy_document
    }
    
    return auth_response

def generate_secret_hash(username):
    message = username + client_id
    dig = hmac.new(client_secret.encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def get_user_email(client, access_token):
    response = client.get_user(AccessToken=access_token)
    attributes = response['UserAttributes']
    email = next((attr['Value'] for attr in attributes if attr['Name'] == 'email'), None)
    
    return email

def check_authentication(username, password):
    secret_hash = generate_secret_hash(username)
    try:
        client = boto3.client('cognito-idp', region_name=region_name)
        
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            },
            ClientId=client_id
        )
        
        access_token = response['AuthenticationResult']['AccessToken']
        email = get_user_email(client, access_token)
        
        return email is not None and "wsc2024.local" in email
    except client.exceptions.NotAuthorizedException as e:
        return False
    except client.exceptions.UserNotFoundException as e:
        return False
    except Exception as e:
        return False

def check_api_name(name):
    users = {
        "jmp": {"competition": "2022", "medal": "gold"},
        "hmj": {"competition": "2021", "medal": "silver"},
        "sjl": {"competition": "2021", "medal": "gold"},
        "thl": {"competition": "2022", "medal": "silver"}
    }
    
    return users.get(name, {"error": "Unknown Users"})
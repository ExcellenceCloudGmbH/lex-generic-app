import os
import requests

def send_email(subject, emails, body):
    url = f"https://{os.getenv('DOMAIN_BASE')}/api/send_email/"
    headers = {
        'Authorization': f"Api-Key {os.getenv('LEX_API_KEY')}",
        'Content-Type': 'application/json'
    }

    # Data to be sent in the POST request
    data = {
        'subject': subject,
        'emails': emails,
        'body': body
    }

    # Making the POST request
    response = requests.post(url, json=data, headers=headers)

    # Check the status code of the response
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed with status code:', response.status_code)
        print('Response:', response.text)
        raise Exception("Failed to send email")

def get_client_roles():
    url = f"https://{os.getenv('DOMAIN_BASE')}/api/get_client_roles/"
    headers = {
        'Authorization': f"Api-Key {os.getenv('LEX_API_KEY')}",
        'Content-Type': 'application/json'
    }
    data = {
        'keycloak_client_id': os.getenv('KEYCLOAK_CLIENT_ID')
    }

    response = requests.get(url, params=data, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print('Failed with status code:', response.status_code)
        print('Response:', response.text)
        raise Exception("Failed to get client roles")
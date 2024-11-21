'''
Sends the output to the RoomBot Telegram chat.
Also sends to the Discord webhook

Maverick Reynolds
08.29.2023
'''

import requests
import json
import configparser

def send_discord(message, webhook):

    #make json to post to the webhook
    data = {
        'content': message
    }
    headers = {
    'Content-Type': 'application/json'
    }
    data = json.dumps(data)

    # Send the POST request to the webhook URL.

    response = requests.post(webhook, data=data, headers=headers)

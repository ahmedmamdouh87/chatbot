from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "test123")
PAGE_ACCESS_TOKEN = os.getenv("EAAKW1GYXQ0IBPHZAK2Sr4npmEEGO2qcwgaFyjVaMxs49jdoBX8btrQjE8L6hnzEIhK9kOZAdDDZAoLVBy6NFLyIYaHIrvkd2ZA2bCzszRRzGA1sGudbdxwFr9tF6oy0GZAtEuDT2hmlp5GsH7EkagJhwVQZBKAIiiQKdvOvNdOXZCAQrZA80uDyVpmZBPET82kY8trrZC0csnrZBgZDZD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional, for future ChatGPT integration

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Invalid verification token'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                if 'message' in event:
                    message_text = event['message'].get('text')
                    if message_text:
                        send_message(sender_id, f"You said: {message_text}")
    return "ok", 200

def send_message(recipient_id, text):
    url = 'https://graph.facebook.com/v17.0/me/messages'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    headers = {'Content-Type': 'application/json'}
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': text}
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    print("Sent:", response.status_code, response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
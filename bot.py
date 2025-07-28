from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import openai

# Load environment variables (only used locally)
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "test123")
PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Facebook webhook verification
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Invalid verification token', 403

# Handle messages from Facebook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data.get('object') == 'page':
        for entry in data['entry']:
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                if 'message' in event and 'text' in event['message']:
                    user_message = event['message']['text']
                    gpt_reply = get_gpt_reply(user_message)
                    send_message(sender_id, gpt_reply)
    return "ok", 200

# Function to get ChatGPT reply
def get_gpt_reply(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, something went wrong."

# Function to send message back to Facebook user
def send_message(recipient_id, text):
    url = 'https://graph.facebook.com/v17.0/me/messages'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    headers = {'Content-Type': 'application/json'}
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': text}
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error sending message: {response.text}")

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

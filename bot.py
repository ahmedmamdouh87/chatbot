import os
import openai
import requests
import traceback
from flask import Flask, request

app = Flask(__name__)

# Load environment variables
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Confirm key presence
print("API Key Exists:", bool(OPENAI_API_KEY))
print("Page Token Exists:", bool(PAGE_ACCESS_TOKEN))

# Set OpenAI key
openai.api_key = OPENAI_API_KEY


def get_chatgpt_response(user_message):
    print("=== Sending to OpenAI ===")
    print("User message:", user_message)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        print("Raw OpenAI Response:", response)
        reply = response['choices'][0]['message']['content']
        print("OpenAI Reply:", reply)
        return reply
    except Exception as e:
        print("OpenAI API call failed:", str(e))
        traceback.print_exc()
        return "Something went wrong while talking to ChatGPT."


def send_message(recipient_id, message_text):
    print(f"=== Sending message to Facebook ===")
    print(f"Recipient: {recipient_id}")
    print(f"Message: {message_text}")

    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(
        "https://graph.facebook.com/v17.0/me/messages",
        params=params,
        headers=headers,
        json=data
    )

    print("Facebook Response:", response.status_code, response.text)


@app.route('/', methods=['GET'])
def home():
    return 'Facebook Messenger bot is running!'


@app.route('/webhook', methods=['GET'])
def verify():
    print("=== Webhook verification attempt ===")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        print("Verification successful")
        return challenge
    print("Verification failed")
    return "Invalid verification token", 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("=== Incoming Facebook Webhook Data ===")
    print(data)

    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    message_text = messaging_event['message']['text']
                    print(f"Received message from {sender_id}: {message_text}")
                    reply_text = get_chatgpt_response(message_text)
                    send_message(sender_id, reply_text)
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

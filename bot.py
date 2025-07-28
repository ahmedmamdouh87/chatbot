import os
import requests
from flask import Flask, request
from openai import OpenAI

# Flask app setup
app = Flask(__name__)

# Load environment variables
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Confirm secrets are loaded
print("API Key Exists:", OPENAI_API_KEY is not None)
print("Page Token Exists:", PAGE_ACCESS_TOKEN is not None)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Generate ChatGPT response
def get_chatgpt_response(user_message):
    print("=== Sending to OpenAI ===")
    print("User message:", user_message)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        print("OpenAI Reply:", reply)
        return reply
    except Exception as e:
        print("OpenAI API call failed:", str(e))
        return "Something went wrong while talking to ChatGPT."

# Send message to Facebook user
def send_message(recipient_id, message_text):
    print(f"=== Sending message to Facebook ===\nRecipient: {recipient_id}\nMessage: {message_text}")
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    r = requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, json=data)
    print("Facebook Response:", r.status_code, r.text)

# Root route for testing
@app.route('/', methods=['GET'])
def home():
    return 'Facebook Messenger bot is running!'

# Webhook verification (GET)
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    print("=== Webhook verification attempt ===")
    if token == VERIFY_TOKEN:
        print("Verification successful")
        return challenge
    print("Verification failed")
    return "Invalid verification token", 403

# Webhook receiver (POST)
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

# Run the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

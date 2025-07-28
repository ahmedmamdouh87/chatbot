import os
from flask import Flask, request
from openai import OpenAI
import requests

app = Flask(__name__)

# Load secrets from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "chatgptbot")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Debug prints to verify environment setup
print("API Key Exists:", bool(OPENAI_API_KEY))
print("Page Token Exists:", bool(PAGE_ACCESS_TOKEN))

def get_chatgpt_response(user_message):
    print("=== Sending to OpenAI ===")
    print("User message:", user_message)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        print("OpenAI Reply:", reply)
        return reply
    except Exception as e:
        print("OpenAI API call failed:", str(e))
        return "Something went wrong while talking to ChatGPT."

def send_message(recipient_id, message_text):
    print(f"Sending message to {recipient_id}: {message_text}")
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    auth = {"access_token": PAGE_ACCESS_TOKEN}
    response = requests.post(
        "https://graph.facebook.com/v17.0/me/messages",
        params=auth,
        json=payload
    )
    print("Message send response:", response.status_code, response.text)

@app.route("/", methods=["GET"])
def home():
    return "Hello, I am a ChatGPT Messenger bot!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verified")
            return challenge, 200
        else:
            return "Verification failed", 403

    elif request.method == "POST":
        payload = request.get_json()
        print("Webhook received:", payload)

        if payload.get("object") == "page":
            for entry in payload.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]
                    if "message" in messaging_event and "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]
                        response_text = get_chatgpt_response(message_text)
                        send_message(sender_id, response_text)
        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

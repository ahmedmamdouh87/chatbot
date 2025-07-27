from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# === Configuration ===
openai.api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key-here")
openai.api_base = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-3.5-turbo"  # or try "mistralai/mistral-7b-instruct"

# === Routes ===
@app.route("/", methods=["GET"])
def index():
    return "Chatbot is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Create completion
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong"}), 500

# === Main entry point ===
if __name__ == "__main__":
    print("OpenRouter Key Loaded:", bool(openai.api_key))
    app.run(host="0.0.0.0", port=10000)

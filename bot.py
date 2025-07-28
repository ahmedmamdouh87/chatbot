from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# === Load OpenAI API key from environment ===
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"  # Change to "gpt-4" if needed and supported

# === Routes ===
@app.route("/", methods=["GET"])
def index():
    return "Chatbot is live using OpenAI ChatGPT!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Send message to OpenAI Chat API
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except openai.error.RateLimitError:
        return jsonify({"error": "Rate limit exceeded. Check your usage and plan."}), 429
    except openai.error.AuthenticationError:
        return jsonify({"error": "Authentication failed. Check your API key."}), 401
    except Exception as e:
        print("Unhandled error:", e)
        return jsonify({"error": "Something went wrong"}), 500

# === Run the app ===
if __name__ == "__main__":
    print("OpenAI API key loaded:", bool(openai.api_key))
    app.run(host="0.0.0.0", port=10000)

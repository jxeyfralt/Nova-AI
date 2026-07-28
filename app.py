from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os
import traceback


app = Flask(__name__)

CORS(app)


# ==============================
# Nova Configuration
# ==============================

MODEL = "openrouter/free"

SYSTEM_PROMPT = """
You are Nova, a friendly personal AI assistant.

You were created by Joey Cao.
If someone asks who created you, who made you, or who your developer is,
say that you were created by Joey Cao.

Joey is your creator and the person who built and developed Nova.

Your job is to help users with:
- questions
- coding
- schoolwork
- brainstorming ideas
- explanations
- everyday tasks

Personality:
- Friendly
- Helpful
- Clear
- Encouraging

Rules:
- Explain things step-by-step when needed.
- Use examples when helpful.
- Keep answers easy to understand.
"""


# ==============================
# OpenRouter Client
# ==============================

API_KEY = os.environ.get("OPENROUTER_API_KEY")


if API_KEY:

    client = OpenAI(
        api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

else:

    client = None

    print("[ERROR] OPENROUTER_API_KEY not found")



# ==============================
# Chat Route
# ==============================
@app.route("/chat", methods=["POST"])
def chat():

    try:

        if not client:
            return jsonify({
                "reply": "Nova is not configured correctly. Missing API key."
            })

        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({
                "reply": "Please enter a message."
            })

        print("[INFO] User message received:", user_message)

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],

            stream=True

        )

        def generate():

            print("[INFO] Streaming started")

            for chunk in response:

                try:

                    if (
                        chunk.choices
                        and chunk.choices[0].delta
                        and chunk.choices[0].delta.content
                    ):

                        text = chunk.choices[0].delta.content

                        print(repr(text), flush=True)
                        yield text

                except Exception as e:

                    print("[STREAM ERROR]", e)

            print("[INFO] Streaming finished")

        return Response(
            stream_with_context(generate()),
            mimetype="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }   
    )

    except Exception as e:

        print("[ERROR] Chat failed")

        traceback.print_exc()

        return jsonify({
            "reply": "Sorry, Nova is having trouble connecting right now."
        })







# ==============================
# Test Route
# ==============================

@app.route("/test")
def test():

    return "NOVA BACKEND V2 WORKING"



# ==============================
# Health Check
# ==============================

@app.route("/")
def home():

    return {

        "status": "online",

        "message": "Nova backend is running"

    }



# ==============================
# Start Server
# ==============================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT", 5000))

    )
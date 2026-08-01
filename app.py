from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os
import traceback
import time
import json

app = Flask(__name__)

CORS(app)


# ==============================
# Nova Configuration
# ==============================

MODEL = "google/gemma-4-26b-a4b-it:free"

SYSTEM_PROMPT = """
You are Nova, a friendly personal AI assistant.

IDENTITY:
- Your name is Nova.
- Your creator and developer is Joey Cao.
- Joey Cao built and developed this AI assistant.

IMPORTANT:
When asked "Who created you?", "Who made you?", or "Who is your developer?",
you must answer:
"I was created by Joey Cao."

Never claim another person created you.
Do not say you don't know.

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
# Nova Memory
# ==============================

MEMORY_FILE = "memory.json"


def load_memory():

    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    except:
        return {
            "name": "",
            "facts": []
        }


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# ==============================
# OpenRouter Client
# ==============================

API_KEY = os.environ.get("OPENROUTER_API_KEY")


if API_KEY:

    client = OpenAI(
        api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://chatnovaai.vercel.app",
            "X-Title": "Nova AI"
        }
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
        if any(word in user_message.lower() for word in [
            "who created you",
            "who made you",
            "who is your developer"
        ]):
            return Response(
                "I was created by Joey Cao, who built and developed Nova AI.",
                mimetype="text/plain"
            )


        print("[INFO] User message received:", user_message)

        start = time.time()


        memory = load_memory()

        memory_text = f"""

        User memory:

        Name:
        {memory.get("name", "")}

        Facts:
        {", ".join(memory.get("facts", []))}

        """


        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + memory_text
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],

            stream=True

        )
        print(f"[TIMING] OpenRouter connected in {time.time() - start:.2f}s")
        def generate():

            print("[INFO] Streaming started")

            first = True

            for chunk in response:

                try:

                    if (
                        chunk.choices
                        and chunk.choices[0].delta
                        and chunk.choices[0].delta.content
                    ):

                        if first:
                            print(f"[TIMING] First token: {time.time() - start:.2f}s")
                            first = False

                        text = chunk.choices[0].delta.content

                        print(repr(text), flush=True)

                        yield text

                except Exception as e:

                    print("[STREAM ERROR]", e)

            print("[INFO] Streaming finished")

        return Response(
            stream_with_context(generate()),
            mimetype="text/plain; charset=utf-8",
            direct_passthrough=True,
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:

        print("[ERROR] Chat failed",e)

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
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests


app = Flask(__name__)

CORS(app)

import os

API_KEY = os.environ.get("OPENROUTER_API_KEY")




@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]


    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers={

            "Authorization": f"Bearer {API_KEY}",

            "Content-Type": "application/json"

        },

        json={

            "model": "openrouter/free",

            "messages": [

                {

                    "role": "system",

                    "content": """
You are Nova, a friendly personal AI assistant.

Help users with:
- questions
- coding
- school
- ideas

Be clear, helpful, and friendly.
"""

                },

                {

                    "role": "user",

                    "content": user_message

                }

            ]

        }

    )


    data = response.json()


    print("OpenRouter response:")
    print(data)



    if "choices" not in data:

        return jsonify({

            "reply": "Nova API error. Check the Flask terminal."

        })



    return jsonify({

        "reply": data["choices"][0]["message"]["content"]

    })



import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
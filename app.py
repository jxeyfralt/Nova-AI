from flask import Flask, request, Response
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)

CORS(app)


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    API_KEY = os.environ.get("OPENROUTER_API_KEY")


    def generate():

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={

                "Authorization": f"Bearer {API_KEY}",

                "Content-Type": "application/json"

            },


            json={

                "model": "openrouter/free",

                "stream": True,


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

            },


            stream=True

        )



    for line in response.iter_lines():

        if line:

            line = line.decode("utf-8")

            print("STREAM:", line)

            if line.startswith("data: "):


                    data = line[6:]



                    if data == "[DONE]":

                        break



                    try:

                        chunk = json.loads(data)


                        text = chunk["choices"][0]["delta"].get(
                            "content",
                            ""
                        )


                        if text:

                            yield text


                    except Exception:

                        pass




    return Response(
        generate(),
        mimetype="text/plain"
    )


@app.route("/test")
def test():
    return "NOVA STREAM VERSION WORKING"

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",5000))
    )
    
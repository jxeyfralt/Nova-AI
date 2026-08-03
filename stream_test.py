from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

@app.route("/chat", methods=["POST"])
def chat():

    message = request.json["message"]

    response = client.chat.completions.create(
        model="google/gemma-4-26b-a4b-it:free",
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True
    )

    def generate():
        for chunk in response:
            if (
                chunk.choices
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                yield chunk.choices[0].delta.content

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(port=5000)
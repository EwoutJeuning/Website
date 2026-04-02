"""
Recipe Generator Web App — No Onion, No Garlic
Flask backend with streaming support via OpenRouter.
"""

import json
import os
from openai import OpenAI
from flask import Flask, Response, request, send_from_directory

app = Flask(__name__, static_folder="static")

SYSTEM_PROMPT = """You are a professional chef who specializes in cooking without onion, garlic, and nuts.
Your recipes MUST NEVER include any of the following ingredients or their derivatives:
- Onion (including green onions, scallions, shallots, leeks, chives)
- Garlic (including garlic powder, garlic salt, garlic oil)
- Nuts of any kind (including peanuts, almonds, cashews, walnuts, pistachios, hazelnuts, pine nuts, pecans, macadamia nuts, nut oils, nut butters)

When asked for a recipe, provide:
1. Recipe name
2. A brief description
3. Ingredients list (with quantities)
4. Step-by-step instructions
5. Optional: tips or substitutions

Use asafoetida (hing) as a flavor substitute when appropriate, and feel free to suggest
other aromatics like fennel, celery, or fresh herbs to add depth of flavor.

Format your response using markdown:
- Use # for the recipe name
- Use ## for section headers (Description, Ingredients, Instructions, Tips)
- Use - for bullet points in the ingredients list
- Use 1. 2. 3. for numbered steps in the instructions"""


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/brother.jpg")
def brother_photo():
    return send_from_directory("static", "brother.jpg")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_request = data.get("request", "").strip()

    if not user_request:
        return {"error": "No request provided."}, 400

    def stream():
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            yield f"data: {json.dumps({'error': 'OPENROUTER_API_KEY environment variable not set.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        try:
            response = client.chat.completions.create(
                model="anthropic/claude-opus-4",
                max_tokens=2048,
                stream=True,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_request},
                ],
            )
            for chunk in response:
                text = chunk.choices[0].delta.content
                if text:
                    yield f"data: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    print("Starting Recipe Generator at http://localhost:5000")
    app.run(debug=True, port=5000)

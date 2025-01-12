from flask import Flask, request, jsonify, make_response
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Environment variables for sensitive data
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

@app.route("/chat", methods=["OPTIONS", "POST"])
def chat():
    if request.method == "OPTIONS":  # Handle CORS preflight request
        return _build_cors_preflight_response()
    elif request.method == "POST":  # Handle actual request
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return _corsify_actual_response(jsonify({"reply": "Please provide a valid query."}))

        api_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": user_message,
        }

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            results = data.get("items", [])

            if results:
                reply = {
                    "results": [
                        {
                            "title": item["title"],
                            "link": item["link"],
                            "image": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src")
                        }
                        for item in results[:3]  # Return top 3 results
                    ]
                }
            else:
                reply = {"reply": "I couldn't find anything relevant to your query."}
        except requests.exceptions.RequestException as e:
            reply = {"reply": "Error connecting to Google Search API."}
        except Exception as e:
            reply = {"reply": f"An unexpected error occurred: {str(e)}"}

        return _corsify_actual_response(jsonify(reply))
    else:
        raise RuntimeError(f"Unexpected method {request.method}")

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS library
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)

# Environment variables for sensitive data
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    user_message = request.json.get("message", "").strip()
    if request.method == "OPTIONS":  # CORS preflight request is handled automatically by CORS library
        return "", 200  # No body needed for OPTIONS request, just return 200 OK

    if not user_message:
        return jsonify({"reply": "Please provide a valid query."})

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

    return jsonify(reply)  # CORS headers will be automatically added by CORS library

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Enable CORS for all origins
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Environment variables for sensitive data
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

@app.route("/chat", methods=["OPTIONS", "POST"])
def chat():
    if request.method == "OPTIONS":
        # Handle preflight request
        print("Received OPTIONS request.")
        response = jsonify({"message": "CORS preflight request successful."})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    print("Received POST request.")
    user_message = request.json.get("message", "").strip()
    print(f"User message: {user_message}")

    if not user_message:
        print("No valid query provided.")
        return jsonify({"reply": "Please provide a valid query."})

    api_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": user_message,
    }

    print(f"Calling Google API with params: {params}")

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        print("Google API response received:", data)

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
            print(f"Top 3 results: {reply}")
        else:
            reply = {"reply": "I couldn't find anything relevant to your query."}
            print("No relevant results found.")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Google Search API: {e}")
        reply = {"reply": "Error connecting to Google Search API."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        reply = {"reply": f"An unexpected error occurred: {str(e)}"}

    response = jsonify(reply)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)

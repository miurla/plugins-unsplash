import json
import os
import requests
from quart import Quart, request, send_file, Response
import quart_cors
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")
assert UNSPLASH_API_KEY, "UNSPLASH_API_KEY environment variable is missing from .env"

UNSPLASH_SEARCH_API = "https://api.unsplash.com/search/photos"

app = quart_cors.cors(Quart(__name__), allow_origin="*")

@app.route("/search", methods=["GET"])
async def search():
    query = request.args.get("query")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 4)

    response = requests.get(
        UNSPLASH_SEARCH_API,
        params={
            "query": query,
            "page": page,
            'per_page': per_page,
            "client_id": UNSPLASH_API_KEY
        }
    )

    if response.status_code != 200:
        return Response(response.text, status=response.status_code)

    data = response.json()
    image_urls = [image["urls"]["regular"] for image in data["results"]]
    return Response(json.dumps(image_urls), status=200)

@app.route("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="text/json")

@app.route("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
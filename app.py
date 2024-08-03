from flask import Flask, render_template, request, jsonify
import base64
import requests
import logging
import os 

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_content', methods=['POST'])
def generate_content():
    try:
        payload = request.json
        logging.debug("Request payload: %s", payload)

        if 'contents' not in payload or not payload['contents']:
            return jsonify({'error': 'Invalid request payload.'}), 400

        contents = payload['contents']
        if len(contents) < 1 or 'parts' not in contents[0] or len(contents[0]['parts']) < 2:
            return jsonify({'error': 'Invalid contents structure.'}), 400

        image_base64 = contents[0]['parts'][2].get('inlineData', {}).get('data')
        if not image_base64:
            return jsonify({'error': 'Image data not found in payload.'}), 400

        image_data = base64.b64decode(image_base64)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        logging.debug("Response JSON: %s", response_json)

        generated_content = response_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')

        if generated_content:
            return jsonify({'generated_content': generated_content})
        else:
            return jsonify({'error': 'Failed to generate content.'}), 500

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        return jsonify({'error': 'Internal Server Error.'}), 500

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, POST'
    return response

if __name__ == '__main__':
    app.run(debug=True)

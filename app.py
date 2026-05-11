from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

SUPADATA_KEY = os.environ.get("SUPADATA_API_KEY")

def extract_video_id(url):
    patterns = [
        r'youtu\.be/([^?&]+)',
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtube\.com/embed/([^?&]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url

@app.route('/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')
    lang = request.args.get('lang', 'en')

    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    res = requests.get(
        'https://api.supadata.ai/v1/transcript',
        params={'url': url, 'lang': lang},
        headers={'x-api-key': SUPADATA_KEY}
    )

    if res.status_code != 200:
        return jsonify({'error': res.json()}), res.status_code

    data = res.json()
    full_text = ' '.join([s['text'] for s in data.get('content', [])])

    return jsonify({
        'video_id': extract_video_id(url),
        'language': data.get('lang', lang),
        'text': full_text,
        'segments': data.get('content', [])
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run()
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
import random
import requests

app = Flask(__name__)

PROXIES = [
    "31.59.20.176:6754:pnllxgdm:46gb5smrbs0w",
    "31.56.127.193:7684:pnllxgdm:46gb5smrbs0w",
    "45.38.107.97:6014:pnllxgdm:46gb5smrbs0w",
    "107.172.163.27:6543:pnllxgdm:46gb5smrbs0w",
    "198.23.243.226:6361:pnllxgdm:46gb5smrbs0w",
    "216.10.27.159:6837:pnllxgdm:46gb5smrbs0w",
    "142.111.67.146:5611:pnllxgdm:46gb5smrbs0w",
    "191.96.254.138:6185:pnllxgdm:46gb5smrbs0w",
    "31.58.9.4:6077:pnllxgdm:46gb5smrbs0w",
    "23.229.19.94:8689:pnllxgdm:46gb5smrbs0w",
]

def get_proxy_session():
    p = random.choice(PROXIES)
    ip, port, user, pwd = p.split(":")
    proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
    session = requests.Session()
    session.proxies = {"http": proxy_url, "https": proxy_url}
    return session

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

    video_id = extract_video_id(url)

    last_error = None
    for _ in range(3):
        try:
            ytt = YouTubeTranscriptApi(http_client=get_proxy_session())
            transcript = ytt.fetch(video_id, languages=[lang, 'en'])
            segments = transcript.to_raw_data()
            full_text = ' '.join([s['text'] for s in segments])
            return jsonify({
                'video_id': video_id,
                'language': lang,
                'text': full_text,
                'segments': segments
            })
        except TranscriptsDisabled:
            return jsonify({'error': 'Transcripts are disabled for this video'}), 404
        except NoTranscriptFound:
            return jsonify({'error': 'No transcript found for this video'}), 404
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({'error': last_error}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run()

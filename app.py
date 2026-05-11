from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

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

    try:
        ytt = YouTubeTranscriptApi()
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
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run()
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

def extract_video_id(url):
    """Extract video ID from any YouTube URL format"""
    patterns = [
        r'youtu\.be/([^?&]+)',
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtube\.com/embed/([^?&]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url  # assume it's already a video ID

@app.route('/transcript', methods=['GET'])
def get_transcript():
    url = request.args.get('url')
    lang = request.args.get('lang', 'en')

    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    video_id = extract_video_id(url)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, 'en'])
        full_text = ' '.join([s['text'] for s in transcript])
        return jsonify({
            'video_id': video_id,
            'language': lang,
            'text': full_text,
            'segments': transcript
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
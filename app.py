from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = "4972eccafemshef0bdd86a834dc1p12e0fcjsn9504907a0150"
RAPIDAPI_HOST = "tiktok-api-fast-reliable-data-scraper.p.rapidapi.com"

@app.route('/')
def home():
    return "TikTok Downloader API is running!"

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format_type = data.get('format', 'mp4')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }

        # RapidAPI তে video info পাঠাও
        api_url = f"https://{RAPIDAPI_HOST}/video/info"
        params = {"video_url": url}

        response = requests.get(api_url, headers=headers, params=params)
        info = response.json()

        if not info or 'data' not in info:
            return jsonify({'error': 'Could not fetch video info. Try another link.'}), 400

        video_data = info['data']

        result = {
            'title': video_data.get('title') or video_data.get('desc', 'TikTok Video'),
            'thumbnail': video_data.get('cover') or video_data.get('thumbnail', ''),
            'duration': video_data.get('duration', 0),
            'formats': []
        }

        # No watermark MP4
        nowm = video_data.get('play') or video_data.get('no_watermark') or video_data.get('video', {}).get('play_addr', {}).get('url_list', [None])[0]
        if nowm:
            result['formats'].append({
                'url': nowm,
                'quality': 'HD No Watermark',
                'ext': 'mp4'
            })

        # With watermark MP4
        wm = video_data.get('wmplay') or video_data.get('watermark')
        if wm:
            result['formats'].append({
                'url': wm,
                'quality': 'With Watermark',
                'ext': 'mp4'
            })

        # MP3 audio
        if format_type == 'mp3':
            audio = video_data.get('music') or video_data.get('audio')
            if audio:
                result['formats'] = [{
                    'url': audio,
                    'quality': 'MP3 Audio',
                    'ext': 'mp3'
                }]

        if not result['formats']:
            return jsonify({'error': 'No download link found. Try another video.'}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

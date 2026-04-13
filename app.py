from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

TIKWM_KEY = "119611d88922a8e7d69322c3a6395eec"

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        res = requests.get(
            'https://www.tikwm.com/api/',
            params={
                'url': url,
                'hd': 1,
                'key': TIKWM_KEY
            },
            headers=headers,
            timeout=15
        )
        info = res.json()

        if info.get('code') != 0 or not info.get('data'):
            return jsonify({'error': 'Could not fetch video. Try another link.'}), 400

        d = info['data']

        video_url = d.get('hdplay') or d.get('play')
        audio_url = d.get('music')
        title = d.get('title', 'TikTok Video')
        thumbnail = d.get('cover', '')
        duration = d.get('duration', 0)

        result = {
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': []
        }

        if format_type == 'mp3' and audio_url:
            result['formats'].append({
                'url': audio_url,
                'quality': 'MP3 Audio',
                'ext': 'mp3'
            })
        else:
            if video_url:
                result['formats'].append({
                    'url': video_url,
                    'quality': 'HD No Watermark',
                    'ext': 'mp4'
                })
            if audio_url:
                result['formats'].append({
                    'url': audio_url,
                    'quality': 'MP3 Audio',
                    'ext': 'mp3'
                })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

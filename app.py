from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = "4972eccafemshef0bdd86a834dc1p12e0fcjsn9504907a0150"

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
        # API 1: tiktok-downloader-without-watermark
        headers1 = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "tiktok-downloader-without-watermark.p.rapidapi.com"
        }
        res1 = requests.get(
            "https://tiktok-downloader-without-watermark.p.rapidapi.com/index",
            headers=headers1,
            params={"url": url}
        )
        info1 = res1.json()

        # Check if this API worked
        video_url = None
        audio_url = None
        title = "TikTok Video"
        thumbnail = ""
        duration = 0

        if info1.get('video') and len(info1['video']) > 0:
            video_url = info1['video'][0]
            audio_url = info1.get('music', [None])[0]
            title = info1.get('title', 'TikTok Video')
            thumbnail = info1.get('cover', '')

        # API 2: tiktok-scraper7 fallback
        if not video_url:
            headers2 = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
            }
            res2 = requests.get(
                "https://tiktok-scraper7.p.rapidapi.com/video/info",
                headers=headers2,
                params={"url": url}
            )
            info2 = res2.json()
            d = info2.get('data', {})
            video_url = d.get('play') or d.get('wmplay')
            audio_url = d.get('music')
            title = d.get('title', 'TikTok Video')
            thumbnail = d.get('cover', '')
            duration = d.get('duration', 0)

        # API 3: tiktok-api-fast fallback
        if not video_url:
            headers3 = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "tiktok-api-fast-reliable-data-scraper.p.rapidapi.com"
            }
            res3 = requests.get(
                "https://tiktok-api-fast-reliable-data-scraper.p.rapidapi.com/video/info",
                headers=headers3,
                params={"video_url": url}
            )
            info3 = res3.json()
            d = info3.get('data', {}) or info3
            video_url = d.get('play') or d.get('download_url') or d.get('video_url')
            audio_url = d.get('music') or d.get('audio')
            title = d.get('title') or d.get('desc', 'TikTok Video')
            thumbnail = d.get('cover') or d.get('thumbnail', '')
            duration = d.get('duration', 0)

        if not video_url and not audio_url:
            return jsonify({'error': 'Could not fetch video. Please subscribe to the API or try another video.'}), 400

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
        elif video_url:
            result['formats'].append({
                'url': video_url,
                'quality': 'HD No Watermark',
                'ext': 'mp4'
            })
            if audio_url and format_type != 'mp3':
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

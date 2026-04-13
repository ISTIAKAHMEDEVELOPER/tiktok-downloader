from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

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
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        if format_type == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
        else:
            ydl_opts['format'] = 'best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            result = {
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'formats': []
            }

            if format_type == 'mp4':
                for f in info.get('formats', []):
                    if f.get('url') and f.get('ext') == 'mp4':
                        result['formats'].append({
                            'url': f['url'],
                            'quality': f.get('format_note', 'HD'),
                            'ext': 'mp4'
                        })

            elif format_type == 'mp3':
                for f in info.get('formats', []):
                    if f.get('url') and 'audio' in f.get('format_note', '').lower():
                        result['formats'].append({
                            'url': f['url'],
                            'quality': 'MP3',
                            'ext': 'mp3'
                        })

            if not result['formats'] and info.get('url'):
                result['formats'].append({
                    'url': info['url'],
                    'quality': 'Best',
                    'ext': format_type
                })

            return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

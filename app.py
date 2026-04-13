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
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.tiktok.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            'extractor_args': {
                'tiktok': {
                    'webpage_download': True,
                }
            }
        }

        if format_type == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            result = {
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'formats': []
            }

            formats = info.get('formats', [])

            if format_type == 'mp4':
                # Try watermark-free first
                for f in formats:
                    furl = f.get('url', '')
                    if furl and f.get('ext') == 'mp4' and 'watermark' not in f.get('format_id', '').lower():
                        result['formats'].append({
                            'url': furl,
                            'quality': f.get('format_note') or f.get('height') and str(f['height'])+'p' or 'HD',
                            'ext': 'mp4'
                        })

                # Fallback
                if not result['formats']:
                    for f in formats:
                        furl = f.get('url', '')
                        if furl and f.get('ext') == 'mp4':
                            result['formats'].append({
                                'url': furl,
                                'quality': f.get('format_note') or 'HD',
                                'ext': 'mp4'
                            })

            elif format_type == 'mp3':
                for f in formats:
                    furl = f.get('url', '')
                    if furl and f.get('acodec') and f.get('acodec') != 'none':
                        result['formats'].append({
                            'url': furl,
                            'quality': 'MP3',
                            'ext': 'mp3'
                        })

            # Final fallback
            if not result['formats']:
                best_url = info.get('url') or info.get('webpage_url')
                if best_url:
                    result['formats'].append({
                        'url': best_url,
                        'quality': 'Best',
                        'ext': format_type
                    })

            if not result['formats']:
                return jsonify({'error': 'Could not extract download link. Try another video.'}), 400

            # Return max 2 formats
            result['formats'] = result['formats'][:2]
            return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from audio_analyzer import analyze_audio
import webbrowser
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 업로드 폴더 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"업로드 폴더 생성: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}

def allowed_file(filename):
    """허용된 파일 형식인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """업로드 폴더가 존재하는지 확인하고 생성"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"업로드 폴더 생성됨: {UPLOAD_FOLDER}")
    except Exception as e:
        logger.error(f"업로드 폴더 생성 중 오류 발생: {str(e)}")
        raise

def cleanup_uploads():
    """uploads 폴더의 모든 파일을 삭제"""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.error(f"파일 삭제 중 오류 발생: {str(e)}")
    except Exception as e:
        logger.error(f"폴더 정리 중 오류 발생: {str(e)}")

def open_browser():
    """기존 브라우저 창을 재사용하여 URL 열기"""
    url = 'http://localhost:5000'
    try:
        # 기본 브라우저의 컨트롤러 가져오기
        browser = webbrowser.get()
        # 기존 창에서 URL 열기
        browser.open(url, new=0, autoraise=True)
    except Exception as e:
        logger.error(f"브라우저 열기 실패: {str(e)}")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '선택된 파일이 없습니다.'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': '지원되지 않는 파일 형식입니다. WAV, MP3, OGG, M4A 파일만 사용 가능합니다.'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"파일 업로드 성공: {filename}")
            return jsonify({'message': '파일이 성공적으로 업로드되었습니다.', 'filename': filename})
            
    except Exception as e:
        logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
        return jsonify({'error': '파일 업로드 중 오류가 발생했습니다.'}), 500

@app.route('/analyze/<filename>', methods=['GET'])
def analyze(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            logger.error(f"파일을 찾을 수 없습니다: {filepath}")
            return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
            
        # 파일 분석
        results = analyze_audio(filepath)
        
        # 분석 완료 후 파일 삭제
        try:
            os.remove(filepath)
            logger.info(f"분석 완료 후 파일 삭제: {filepath}")
        except Exception as e:
            logger.error(f"파일 삭제 중 오류 발생: {str(e)}")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ensure_upload_folder()
    open_browser()  # 브라우저를 한 번만 열기
    app.run(host='localhost', port=5000, debug=False)  # 디버그 모드 비활성화 
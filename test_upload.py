import requests
import os
from pydub import AudioSegment
import numpy as np

def create_test_audio():
    # 3초 길이의 테스트 오디오 파일 생성
    sample_rate = 44100
    duration = 3  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    
    # numpy array를 AudioSegment로 변환
    audio = AudioSegment(
        note.tobytes(), 
        frame_rate=sample_rate,
        sample_width=2,  # 16-bit
        channels=1
    )
    
    # m4a 형식으로 저장
    output_path = "test_audio.m4a"
    audio.export(output_path, format="m4a")
    return output_path

def test_upload():
    # 테스트 오디오 파일 생성
    audio_path = create_test_audio()
    
    # 파일 업로드
    url = "http://localhost:5000/upload"
    files = {'file': open(audio_path, 'rb')}
    
    try:
        response = requests.post(url, files=files)
        print("업로드 응답:", response.json())
        
        if response.ok:
            # 분석 요청
            analyze_url = "http://localhost:5000/analyze"
            analyze_data = response.json()
            analyze_response = requests.post(analyze_url, json=analyze_data)
            print("분석 응답:", analyze_response.json())
    except Exception as e:
        print("오류 발생:", str(e))
    finally:
        # 테스트 파일 삭제
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    test_upload() 
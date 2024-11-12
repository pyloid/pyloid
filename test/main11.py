from pyloid.pyloid import Pyloid
from pyloid.utils import is_production, get_production_path, get_absolute_path
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaRecorder, QMediaFormat, QMediaCaptureSession, QAudioInput, QWindowCapture
from PySide6.QtCore import QUrl, QTimer
from datetime import datetime
import os
import wave
import numpy as np

app = Pyloid(app_name="Pyloid-App", single_instance=True)

audio_input = QAudioInput()
audio_output = QAudioOutput()

print(audio_input.device().id().toBase64())
print(audio_output.device().id().toBase64())

if is_production():
    app.set_icon(os.path.join(get_production_path(), "icon.ico"))
    app.set_tray_icon(os.path.join(get_production_path(), "icon.ico"))
else:
    app.set_icon("assets/icon.ico")
    app.set_tray_icon("assets/icon.ico")

win = app.create_window("main2")

win.set_dev_tools(True)

if is_production():
    win.load_file(os.path.join(get_production_path(), "file/index5.html"))
else:
    win.load_file("file/index5.html")

win.add_shortcut("ctrl+a", lambda: print("ctrl+a"))

# 녹음 관련 설정
capture_session = QMediaCaptureSession()
audio_input = QAudioInput()
recorder = QMediaRecorder()

capture_session.setAudioInput(audio_input)
capture_session.setRecorder(recorder)

# 오디오 레벨 모니터링을 위한 설정
recorder.durationChanged.connect(lambda duration: check_duration(duration))

def check_duration(duration):
    print(f"현재 녹음 시간: {duration}ms")
    # 녹음 시간이 1분을 초과하면 자동 중지
    if duration > 60000:  # duration은 밀리초 단위
        stop_recording()
        print("최대 녹음 시간 초과로 녹음이 중지되었습니다.")

# 녹음 파일 포맷 설정
recorder.setMediaFormat(QMediaFormat.FileFormat.Wave)
recorder.setQuality(QMediaRecorder.Quality.HighQuality)

# 녹음 시작 단축키
win.add_shortcut("ctrl+r", lambda: start_recording())
# 녹음 중지 단축키
win.add_shortcut("ctrl+s", lambda: stop_recording())

def start_recording():
    global timer
    # 타이머 생성
    timer = QTimer()
    timer.setInterval(1000)  # 1초 간격
    timer.timeout.connect(save_audio_chunk)
    
    # 녹음 파일 기본 경로 설정
    global base_timestamp
    base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # recordings 폴더 생성
    os.makedirs(get_absolute_path("recordings"), exist_ok=True)
    
    # 녹음 시작
    recorder.record()
    timer.start()
    print("Recording started...")

def save_audio_chunk():
    # 현재 녹음 중지
    recorder.stop()
    
    # 새로운 파일명 생성
    timestamp = datetime.now().strftime("%H%M%S")
    file_path = get_absolute_path(f"recordings/recording_{base_timestamp}_{timestamp}.wav")
    
    print(QUrl.fromLocalFile(file_path).toLocalFile())
    # 새 녹음 시작
    recorder.setOutputLocation(QUrl.fromLocalFile(file_path))
    recorder.record()
    
    # 이전 파일의 평균 볼륨 계산 (지연 시간 증가)
    QTimer.singleShot(100, lambda: calculate_volume(QUrl.fromLocalFile(file_path).toLocalFile()))  # 100ms
######################
# 보니까 파일 생성이 좀 느리다 기각
###################
def calculate_volume(file_path):
    try:
        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            print(f"파일이 아직 생성되지 않았습니다: {file_path}")
            return
            
        with wave.open(file_path, 'rb') as wav_file:
            # 오디오 데이터 읽기
            signal = wav_file.readframes(-1)
            signal = np.frombuffer(signal, dtype=np.int16)
            
            # 평균 볼륨 계산
            average_volume = np.abs(signal).mean()
            print(f"Average volume for {os.path.basename(file_path)}: {average_volume:.2f}")
    except Exception as e:
        print(f"볼륨 계산 중 오류 발생: {e}")

def stop_recording():
    timer.stop()
    recorder.stop()
    print("Recording stopped and saved.")

win.show_and_focus()

app.run()
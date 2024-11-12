from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaRecorder, QMediaFormat, QMediaCaptureSession, QAudioInput, QWindowCapture
from PySide6.QtCore import QUrl
import sys

class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("오디오 플레이어")
        self.setGeometry(100, 100, 300, 150)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 미디어 플레이어 및 오디오 출력 설정
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # 컨트롤 버튼 생성
        self.play_button = QPushButton("재생")
        self.stop_button = QPushButton("정지")
        
        # 버튼 이벤트 연결
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.clicked.connect(self.stop_audio)

        # 레이아웃에 버튼 추가
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)

        # 오디오 파일 설정 (예시 경로)
        self.player.setSource(QUrl.fromLocalFile("response.wav"))
        self.audio_output.setVolume(50)

        # 녹음 관련 컴포넌트 설정
        self.audio_input = QAudioInput()
        self.recorder = QMediaRecorder()
        self.capture_session = QMediaCaptureSession()
        self.capture_session.setAudioInput(self.audio_input)
        self.capture_session.setRecorder(self.recorder)

        # 녹음 버튼 추가
        self.record_button = QPushButton("녹음")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        # 녹음 파일 카운터 추가
        self.recording_counter = 1
        
        # 녹음 포맷 설정
        self.recorder.setQuality(QMediaRecorder.Quality.HighQuality)
        self.recorder.setMediaFormat(QMediaFormat.FileFormat.Wave)
        self.update_recording_filename()
        
        # 녹음 완료 시그널 연결
        self.recorder.recorderStateChanged.connect(self.on_recorder_state_changed)

    def play_audio(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setText("재생")
        else:
            self.player.play()
            self.play_button.setText("일시정지")

    def stop_audio(self):
        self.player.stop()
        self.play_button.setText("재생")

    def update_recording_filename(self):
        filename = f"recording_{self.recording_counter}.wav"
        self.recorder.setOutputLocation(QUrl.fromLocalFile(f"C:/Users/aaaap/Documents/pyloid/pyloid/{filename}"))
        
    def on_recorder_state_changed(self, state):
        if state == QMediaRecorder.RecorderState.StoppedState:
            print(f"녹음이 저장되었습니다: recording_{self.recording_counter}.wav")
            self.recording_counter += 1
            self.update_recording_filename()

    def toggle_recording(self):
        if self.recorder.recorderState() == QMediaRecorder.RecorderState.RecordingState:
            self.recorder.stop()
            self.record_button.setText("녹음")
        else:
            self.recorder.record()
            self.record_button.setText("녹음 중지")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = AudioPlayer()
    
    player.show()
    sys.exit(app.exec())

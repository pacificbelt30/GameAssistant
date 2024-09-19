import pyaudio
import wave
import faster_whisper
# import keyboard
from pynput import keyboard
import ffmpeg
import time
import os

class SpeechRecognition:
    def __init__(self, model='small', temp_dir: str='./temp/'):
        # faster_whisper のモデルをロード
        self.model = faster_whisper.WhisperModel(model, device="cuda",device_index=1, compute_type="float32")

        # PyAudio の設定
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.DEVICE = 0
        self.RATE = 16000  # Whisper モデルのサンプリングレートに合わせる

        # PyAudio の初期化
        self.p = pyaudio.PyAudio()
        if os.path.exists(temp_dir) and os.path.isfile(temp_dir):
            raise FileExistsError(f'すでに {temp_dir} ファイルが存在します')
        elif not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir


    def speech(self):
        # ストリームを開く
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.DEVICE,
                        frames_per_buffer=self.CHUNK)
        print("録音開始... Ctrl+C で終了")
        # キーボードリスナーの設定
        def on_press(key):
            if key == keyboard.Key.esc:  # Esc キーで終了
                return False  # リスナーを停止
        # 音声データを格納するリスト
        frames = []
        with keyboard.Listener(on_press=on_press) as listener:
            try:
                while listener.running:
                    data = stream.read(self.CHUNK)
                    frames.append(data)

            except:
                import traceback
                traceback.print_exc()
                print("\n録音終了")

            finally:
                print("finally")
                # ストリームを閉じる
                stream.stop_stream()
                stream.close()
                self.p.terminate()
                self.save_wave(frames)
                self.noise_reduction()
                self.whisper()

    def save_wave(self, frames, filename: str='test1.wav'):
        start = time.time()
        # 音声データを WAV ファイルに保存
        wf = wave.open(os.path.join(self.temp_dir, filename), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        end = time.time()
        print('save wav: ==>', end-start, '[s]')

    def noise_reduction(self, input_file: str='test1.wav', output_file: str='test1o.wav'):
        # WAV ファイルを読み込み
        # 音声認識を実行
        start = time.time()
        input = ffmpeg.input(os.path.join(self.temp_dir, input_file))
        output = input.audio.filter('volume', '10dB').filter('lowpass',1000).filter('highpass', 100)
        output.output(os.path.join(self.temp_dir, output_file)).run(overwrite_output=True)
        # ffmpeg.overwrite_output(output, 'test1o.wav')
        # ffmpeg.output(output, 'test1o.wav', 'y')
        end = time.time()
        print('processing wav: ==>', end-start, '[s]')

    def whisper(self, filename: str='test1o.wav'):
        start = time.time()
        segments, info = self.model.transcribe(os.path.join(self.temp_dir, filename), beam_size=5, language="ja")
        end = time.time()
        print('whisper: ==>', end-start, '[s]', segments)

        # 認識結果を表示
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")


    @classmethod
    def look_for_audio_input():
        """
        デバイス上でのオーディオ系の機器情報を表示する
        """
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            print(pa.get_device_info_by_index(i))
            print()
        pa.terminate()


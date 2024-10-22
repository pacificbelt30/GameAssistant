from typing import List
import pyaudio
import wave
import faster_whisper
# import keyboard
from pynput import keyboard
import ffmpeg
import time
import os
import webrtcvad
from reazonspeech.k2.asr import load_model, transcribe, audio_from_path, audio_from_numpy
import numpy as np

import queue

audio_queue = queue.Queue()

class SpeechCapture:
    def __init__(self):
        # PyAudio の設定
        self.CHUNK = 480
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.DEVICE = 0
        self.RATE = 16000  # Whisper モデルのサンプリングレートに合わせる

    def speech_vad(self):
        # VAD の初期化
        vad = webrtcvad.Vad(3)  # 3 は最も感度の高いモード
        # PyAudio の初期化
        self.p = pyaudio.PyAudio()
        # ストリームを開く
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.DEVICE,
                        frames_per_buffer=self.CHUNK)

        print("待機中...")
        # 音声データを格納するリスト
        frames = []
        silent_frames = []

        # キーボードリスナーの設定
        def on_press(key):
            if key == keyboard.Key.esc:  # Esc キーで終了
                return False  # リスナーを停止

        while True:
            # 録音前の発話検知
            before_data = None
            while True:
                data = stream.read(self.CHUNK)

                # 音声区間を検出
                is_speech = vad.is_speech(data, self.RATE)

                # 音声区間が始まったら録音開始
                if is_speech:
                    print("録音開始")
                    if before_data is not None:
                        frames.append(before_data)
                    frames.append(data)
                    break
                before_data = data


            # 発話開始後の録音
            try:
                # 1s 程度無音が続いた場合に終了する
                while len(silent_frames) < self.RATE//self.CHUNK:
                    data = stream.read(self.CHUNK)
                    is_speech = vad.is_speech(data, self.RATE)
                    if not is_speech:
                        silent_frames.append(data)
                    else:
                        if silent_frames != []:
                            for frame in silent_frames: frames.append(frame)
                            silent_frames = []
                        frames.append(data)
            except:
                import traceback
                traceback.print_exc()
                print("\n録音終了")
                break
            finally:
                print("finally")
                # ストリームを閉じるべきかそのまま使うかは要相談
                # stream.stop_stream()
                # stream.close()
                # self.p.terminate()
                # self.save_wave(frames)
                # self.noise_reduction()

                # 音声をそのまま Queue に格納
                if frames != []:
                    global audio_from_numpy
                    audio_queue.put(frames)
                    frames = []

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


class SpeechRecognition:
    def __init__(self, model:str='reasonspeech', temp_dir: str='./temp/'):
        # PyAudio の設定
        self.CHUNK = 480
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.DEVICE = 0
        self.RATE = 16000  # Whisper モデルのサンプリングレートに合わせる

        # faster_whisper or reasonspeech k2 v2 のモデルをロード
        if model == 'reasonspeech':
            self.model = ReasonSpeechK2(rate=self.RATE)
        else:
            self.model = FasterWhisper(model_size='small', index=0)

        if os.path.exists(temp_dir) and os.path.isfile(temp_dir):
            raise FileExistsError(f'すでに {temp_dir} ファイルが存在します')
        elif not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir


    def speech_vad(self):
        # VAD の初期化
        vad = webrtcvad.Vad(3)  # 3 は最も感度の高いモード
        # PyAudio の初期化
        self.p = pyaudio.PyAudio()
        # ストリームを開く
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.DEVICE,
                        frames_per_buffer=self.CHUNK)

        print("待機中...")
        # 音声データを格納するリスト
        frames = []

        # キーボードリスナーの設定
        def on_press(key):
            if key == keyboard.Key.esc:  # Esc キーで終了
                return False  # リスナーを停止

        before_data = None
        while True:
            data = stream.read(self.CHUNK)

            # 音声区間を検出
            is_speech = vad.is_speech(data, self.RATE)

            # 音声区間が始まったら録音開始
            if is_speech:
                print("録音開始")
                if before_data is not None:
                    frames.append(before_data)
                frames.append(data)
                break
            before_data = data

        print("録音開始... Ctrl+C で終了")
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
                self.model.inference_from_path(os.path.join(self.temp_dir, 'test1.wav'))

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


class FasterWhisper():
    def __init__(self, model_size: str='small', index: int=0):
        self.model = faster_whisper.WhisperModel(model_size, device="cuda",device_index=index, compute_type="float32")

    def inference_from_path(self, filename: str) -> str:
        start = time.time()
        segments, info = self.model.transcribe(filename, beam_size=5, language="ja")
        end = time.time()
        print('whisper: ==>', end-start, '[s]', segments)

        text = ''
        # 認識結果を表示
        for segment in segments:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            text += segment.text
        return text

    def inference(self, audio: List[List[int]]) -> str:
        return ''

# reference https://research.reazon.jp/projects/ReazonSpeech/api/reazonspeech.k2.asr.html#reazonspeech.k2.asr.transcribe
class ReasonSpeechK2:
    def __init__(self, rate: int):
        self.RATE = rate
        self.model = load_model(precision='int8')

    def inference_from_path(self, filename: str) -> str:
        audio = audio_from_path(filename)
        ret = transcribe(self.model, audio)
        print(ret)
        return ret

    def inference(self, audio: List[List[int]]) -> str:
        audio = audio_from_numpy(np.array(audio), self.RATE)
        ret = transcribe(self.model, audio)
        print(ret)
        return ret.text


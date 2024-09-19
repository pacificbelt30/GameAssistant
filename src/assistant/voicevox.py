import requests
import simpleaudio
# import json
import os

# VoiceVox Engine の API を使う
class VoiceVoxWrapper:
    def __init__(self, base_url: str='http://127.0.0.1:50021'):
        self.base_url = base_url
        temp_dir = './temp/'
        if os.path.exists(temp_dir) and os.path.isfile(temp_dir):
            raise FileExistsError(f'すでに {temp_dir} ファイルが存在します')
        elif not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir

    def create_query_text(self, speaker_id: int=0, text :str="これはテストです。"):
        payload = {'speaker': speaker_id, 'text': text}
        r = requests.post(f'{self.base_url}/audio_query', params=payload)
        print(r.json())
        res = r.json()
        return res

    def create_voice(self, speaker_id: int=0, text: str="これはテストです。"):
        res = self.create_query_text(speaker_id, text)
        payload = res
        print(payload)
        headers = {'content-type': 'application/json'}
        r = requests.post(f'{self.base_url}/synthesis', params={'speaker': speaker_id}, json=payload, headers=headers)
        with open(os.path.join(self.temp_dir, 'audio.wav'), 'wb') as f:
            f.write(r.content)

    def play_sound(self, wav: str='audio.wav'):
        wav_obj = simpleaudio.WaveObject.from_wave_file(os.path.join(self.temp_dir, wav))
        play_obj = wav_obj.play()
        play_obj.wait_done()


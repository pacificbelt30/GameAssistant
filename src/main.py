import sys
import time
import threading
import queue
from assistant.screenshot import capture_screen, get_capture
from assistant.ai import AIAssistant
from assistant.whisper import SpeechRecognition, SpeechCapture
from assistant.voicevox import VoiceVoxWrapper

import langchain
langchain.debug = False
DEBUG = False

if DEBUG:
    provider = 'google'
    use_img = False
    ai = AIAssistant(provider=provider, model='gemini-1.5-flash-002', use_img=use_img)
    prompt = '日本の古典的落語である「寿限無」について、3文程度で解説してください。'
    for ch in ai.ai_eval_stream(prompt):
        print(ch)
    exit(0)

if __name__ == '__main__':
    use_img = False
    # use_img = True
    provider = 'google'
    # provider = 'openai'
    speaker = 2

    # capture_screen((0,0), 1000, 900)

    # AI Assistant initialize
    # ai = AIAssistant(provider='local')
    # ai = AIAssistant(provider=provider, model='gemini-1.5-flash-002', use_img=use_img)
    # ai = AIAssistant(provider=provider, model='gpt-4o-mini', use_img=use_img)
    ai = AIAssistant(provider=provider, model='gemini-1.5-flash-8b', use_img=use_img)
    # ai.set_images(['data/zundamon.png'])
    if provider == 'local':
        ai.ai_eval('Warmup')

    # voicevox setup
    vv = VoiceVoxWrapper(str(sys.argv[1]))
    wave_queue = queue.Queue()
    vv.set_queue(wave_queue)

    # Recorder setup
    sc = SpeechCapture(0.75)

    # SpeechRecognition setup
    output_queue = queue.Queue()
    sr = SpeechRecognition(output_queue=output_queue)
    # sr_thread = threading.Thread(target=sr.)

    # start threading
    vv_thread = threading.Thread(target=vv.inf_loop_play_sound, daemon=True)
    sc_thread = threading.Thread(target=sc.speech_vad, daemon=True)
    sr_thread = threading.Thread(target=sr.inf_loop_speech_recognition, daemon=True)
    sc_thread.start()
    sr_thread.start()
    vv_thread.start()
    # sc_thread.join()


    # AI Conversation
    while True:
        text = output_queue.get()
        if use_img:
            img = get_capture((800, 180), 300, 400)['img']
            ai.set_image_from_b64(img)
        # prompt = '日本の古典的落語である「寿限無」について、3文程度で解説してください。'
        start, end = 0, 0
        for ch in ai.ai_eval_stream(text):
            start = time.time()
            vv.create_voice(text=ch['result'], speaker_id=speaker)
            # vv.play_sound('audio.wav')
            end = time.time()
            print('create_voice タイム計測', end-start)
        # res = ai.ai_eval(text)


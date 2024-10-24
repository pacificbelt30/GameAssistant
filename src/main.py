import sys
import threading
import queue
from assistant.screenshot import capture_screen, get_capture
from assistant.ai import AIAssistant
from assistant.whisper import SpeechRecognition, SpeechCapture
from assistant.voicevox import VoiceVoxWrapper

if __name__ == '__main__':
    use_img = True
    provider = 'google'
    # capture_screen((0,0), 1000, 900)
    # ai = AIAssistant(provider='local')
    ai = AIAssistant(provider=provider, model='gemini-1.5-flash-002', use_img=use_img)
    # ai.set_images(['data/zundamon.png'])
    if provider == 'local':
        ai.ai_eval('Warmup')
    vv = VoiceVoxWrapper(str(sys.argv[1]))
    sc = SpeechCapture()
    sc_thread = threading.Thread(target=sc.speech_vad, daemon=True)
    output_queue = queue.Queue()
    sr = SpeechRecognition(output_queue=output_queue)
    # sr_thread = threading.Thread(target=sr.)
    sr_thread = threading.Thread(target=sr.inf_loop_speech_recognition, daemon=True)
    sc_thread.start()
    sr_thread.start()
    # sc_thread.join()
    while True:
        text = output_queue.get()
        if use_img:
            img = get_capture((800, 180), 300, 400)['img']
            ai.set_image_from_b64(img)
        res = ai.ai_eval(text)
        vv.create_voice(text=res['result'], speaker_id=2)
        vv.play_sound('audio.wav')


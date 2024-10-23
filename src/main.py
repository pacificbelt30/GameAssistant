import sys
import threading
import queue
from assistant.screenshot import capture_screen
from assistant.ai import AIAssistant
from assistant.whisper import SpeechRecognition, SpeechCapture
from assistant.voicevox import VoiceVoxWrapper

if __name__ == '__main__':
    # capture_screen((0,0), 1000, 900)
    ai = AIAssistant(provider='local')
    # ai = AIAssistant(provider='google', model='gemini-1.5-flash-002')
    # ai.set_images(['data/zundamon.png'])
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
        res = ai.ai_eval(output_queue.get())
        vv.create_voice(text=res['result'], speaker_id=2)
        vv.play_sound('audio.wav')


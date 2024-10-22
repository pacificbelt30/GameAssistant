import threading
from assistant.screenshot import capture_screen
from assistant.ai import AIAssistant
from assistant.whisper import SpeechRecognition, SpeechCapture

if __name__ == '__main__':
    # capture_screen((0,0), 1000, 900)
    # ai = AIAssistant(provider='test')
    # ai.set_images(['data/screenshot.png'])
    # ai.ai_eval()
    sc = SpeechCapture()
    sc_thread = threading.Thread(target=sc.speech_vad, daemon=True)
    sr = SpeechRecognition()
    # sr_thread = threading.Thread(target=sr.)
    sc_thread.start()
    # sc_thread.join()
    while True:
        sr.process_queue_audio()


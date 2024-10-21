from assistant.screenshot import capture_screen
from assistant.ai import AIAssistant
from assistant.whisper import SpeechRecognition

if __name__ == '__main__':
    # capture_screen((0,0), 1000, 900)
    # ai = AIAssistant(provider='test')
    # ai.set_images(['data/screenshot.png'])
    # ai.ai_eval()
    sr = SpeechRecognition()
    for i in range(4):
        sr.speech_vad()


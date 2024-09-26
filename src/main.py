from assistant.screenshot import capture_screen
from assistant.ai import AIAssistant

if __name__ == '__main__':
    # capture_screen((0,0), 1000, 900)
    ai = AIAssistant()
    # ai = AIAssistant(provider='google', model='gemini-1.5-flash-002')
    ai.set_images(['data/zundamon.png'])
    ai.ai_eval('画像の内容を説明してください。')


from typing import Optional

from translator import translate_en_to_vi
from text_to_speech import speak


class ChatbotTranslatorMini:
    """
    Minimal pipeline:
    - Input: English text
    - Translate: English -> Vietnamese
    - Output: text and optional voice
    """

    def __init__(self, voice_output: bool = False, tts_rate: int = 160):
        self.voice_output = voice_output
        self.tts_rate = tts_rate

    def respond_text(self, input_en: str) -> Optional[str]:
        vi = translate_en_to_vi(input_en)
        if vi and self.voice_output:
            speak(vi, rate=self.tts_rate, prefer_vi=True)
        return vi

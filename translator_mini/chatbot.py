from typing import Optional

from translator_mini.translator import translate_en_to_vi
from translator_mini.text_to_speech import speak


class ChatbotTranslatorMini:
    """
    Minimal pipeline:
    - Input: English text
    - Translate: English -> Vietnamese
    - Output: text and optional voice
    """

    def __init__(self, voice_output: bool = False, tts_rate: int = 140, use_gtts: bool = True):
        self.voice_output = voice_output
        self.tts_rate = tts_rate
        self.use_gtts = use_gtts

    def respond_text(self, input_en: str) -> Optional[str]:
        vi = translate_en_to_vi(input_en)
        if vi and self.voice_output:
            speak(vi, rate=self.tts_rate, prefer_vi=True, use_gtts=self.use_gtts)
        return vi

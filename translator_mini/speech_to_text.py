"""
Speech-to-Text Module for Chatbot Translator Mini
Supports English (en-US) and Vietnamese (vi-VN) recognition.
"""

import sys
from typing import Optional, List, Tuple

try:
    import speech_recognition as sr
except ImportError as e:
    raise RuntimeError("speech_recognition is required. Install with: pip install SpeechRecognition") from e


def list_microphones() -> List[Tuple[int, str]]:
    """
    Returns a list of available microphones as tuples: (index, name)
    """
    mics = sr.Microphone.list_microphone_names()
    return list(enumerate(mics))


def listen_and_recognize(
    mic_index: Optional[int] = None,
    language: str = "en-US",
    timeout: float = 5.0,
    phrase_time_limit: Optional[float] = 10.0,
    energy_threshold: int = 300,
) -> Optional[str]:
    """
    Listen from the selected microphone and recognize speech using Google's free Web Speech API.

    Args:
        mic_index: index from list_microphones() or None for default
        language: BCP-47 code like 'en-US', 'vi-VN', or 'auto' (tries en-US first, then vi-VN)
        timeout: seconds to wait for phrase start
        phrase_time_limit: max seconds to record phrase
        energy_threshold: ambient energy threshold

    Returns:
        Recognized text or None if not understood.
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy_threshold

    mic_kwargs = {"device_index": mic_index} if mic_index is not None else {}

    try:
        with sr.Microphone(**mic_kwargs) as source:
            print("[STT] Calibrating for ambient noise…")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("[STT] Listening… Speak now.")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        print("[STT] No speech detected within timeout.")
        return None
    except Exception as e:
        print(f"[STT] Microphone error: {e}")
        return None

    # Handle "auto" language detection
    if language == "auto":
        # Try English first
        text = _recognize_audio(recognizer, audio, "en-US")
        if text:
            return text
        # Then try Vietnamese
        print("[STT] Trying Vietnamese recognition...")
        return _recognize_audio(recognizer, audio, "vi-VN")
    else:
        return _recognize_audio(recognizer, audio, language)


def _recognize_audio(recognizer: sr.Recognizer, audio: sr.AudioData, language: str) -> Optional[str]:
    """
    Internal function to recognize audio with specified language.
    """
    try:
        print(f"[STT] Recognizing ({language})…")
        text = recognizer.recognize_google(audio, language=language)
        print(f"[STT] Heard: {text}")
        return text
    except sr.UnknownValueError:
        print(f"[STT] Could not understand audio ({language}).")
        return None
    except sr.RequestError as e:
        print(f"[STT] API unavailable or quota exceeded: {e}")
        return None


def listen_multilingual(
    mic_index: Optional[int] = None,
    languages: List[str] = ["en-US", "vi-VN"],
    timeout: float = 5.0,
    phrase_time_limit: Optional[float] = 10.0,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Listen and try to recognize in multiple languages.
    
    Returns:
        Tuple of (recognized_text, detected_language) or (None, None)
    """
    recognizer = sr.Recognizer()
    
    mic_kwargs = {"device_index": mic_index} if mic_index is not None else {}
    
    try:
        with sr.Microphone(**mic_kwargs) as source:
            print("[STT] Calibrating...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[STT] Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        print("[STT] No speech detected.")
        return None, None
    except Exception as e:
        print(f"[STT] Microphone error: {e}")
        return None, None
    
    # Try each language
    for lang in languages:
        try:
            text = recognizer.recognize_google(audio, language=lang)
            if text:
                print(f"[STT] Recognized ({lang}): {text}")
                return text, lang
        except (sr.UnknownValueError, sr.RequestError):
            continue
    
    print("[STT] Could not recognize in any language.")
    return None, None

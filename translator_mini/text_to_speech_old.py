from typing import Optional

try:
    import pyttsx3
except ImportError as e:
    raise RuntimeError("pyttsx3 is required. Install with: pip install pyttsx3") from e


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine


def _choose_vi_voice(engine) -> Optional[str]:
    """
    Try to find a Vietnamese voice id from available voices.
    Returns voice id or None if not found.
    """
    for v in engine.getProperty("voices"):
        name = (v.name or "").lower()
        vid = (v.id or "").lower()
        langs = [str(x).lower() for x in getattr(v, "languages", [])]
        if "vi" in vid or "vietnam" in name:
            return v.id
        if any("vi" in l for l in langs):
            return v.id
    return None


def speak(text: str, rate: int = 160, volume: float = 1.0, prefer_vi: bool = True) -> bool:
    """
    Speak the given text via system TTS.
    On Ubuntu, pyttsx3 uses eSpeak/ALSA (works on ARM/Orange Pi).

    - rate: words per minute
    - volume: 0.0 to 1.0
    - prefer_vi: try to select Vietnamese voice if available

    Returns True if queued successfully.
    """
    if not text:
        return True

    engine = _get_engine()
    try:
        engine.setProperty("rate", rate)
        engine.setProperty("volume", max(0.0, min(1.0, volume)))

        if prefer_vi:
            vi_voice = _choose_vi_voice(engine)
            if vi_voice:
                engine.setProperty("voice", vi_voice)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[TTS] Error: {e}")
        return False

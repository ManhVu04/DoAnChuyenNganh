from typing import Optional

try:
    from deep_translator import GoogleTranslator
except ImportError as e:
    raise RuntimeError("deep-translator is required. Install with: pip install deep-translator") from e


def translate_en_to_vi(text: str) -> Optional[str]:
    """
    Translate English text to Vietnamese using Google (via deep-translator).
    Returns translated text or None if failed.
    """
    if not text:
        return ""

    try:
        translator = GoogleTranslator(source="en", target="vi")
        return translator.translate(text)
    except Exception as e:
        print(f"[Translate] Error: {e}")
        return None

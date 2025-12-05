from typing import Optional
import os
import tempfile
import time

try:
    import pyttsx3
except ImportError as e:
    raise RuntimeError("pyttsx3 is required. Install with: pip install pyttsx3") from e

# Try to import gTTS for better Vietnamese voice
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("[TTS] gTTS not available. Install with: pip install gtts")

# Try pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[TTS] pygame not available. Install with: pip install pygame")


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


def _play_audio_pygame(filepath: str, timeout_s: float = 15.0) -> bool:
    """
    Play audio file using pygame.
    CRITICAL: Fully quit and reinit pygame for each playback to avoid stuck state.
    """
    if not PYGAME_AVAILABLE:
        return False
    
    try:
        # ALWAYS fully quit pygame first (not just mixer)
        try:
            pygame.mixer.music.stop()
        except:
            pass
        try:
            pygame.mixer.music.unload()
        except:
            pass
        try:
            pygame.mixer.quit()
        except:
            pass
        try:
            pygame.quit()
        except:
            pass
        
        # Small delay to ensure full cleanup
        time.sleep(0.15)
        
        # Fresh init
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Load and play
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        # Wait for playback with timeout
        start_time = time.time()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            if time.time() - start_time > timeout_s:
                pygame.mixer.music.stop()
                break
        
        # Full cleanup after playback
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"[TTS] pygame playback error: {e}")
        try:
            pygame.quit()
        except:
            pass
        return False


def speak_gtts(text: str, lang: str = "vi", timeout_s: float = 15.0) -> bool:
    """
    Speak using Google TTS (better Vietnamese voice).
    Requires: pip install gtts pygame
    
    Args:
        text: Text to speak
        lang: Language code ('vi' or 'en')
        timeout_s: Max playback time
    
    Fully reinits pygame each call to prevent stuck state between turns.
    """
    if not GTTS_AVAILABLE:
        print("[TTS] gTTS not available")
        return False
    
    if not PYGAME_AVAILABLE:
        print("[TTS] pygame not available for audio playback")
        return False

    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name

        # Generate speech using Google TTS
        print(f"[TTS] 🔊 Generating audio ({lang}): '{text[:30]}...'")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_file)

        # Play audio
        success = _play_audio_pygame(temp_file, timeout_s)
        
        if success:
            print("[TTS] ✓ Audio playback complete")
        else:
            print("[TTS] ✗ Audio playback failed")
            
        return success
        
    except Exception as e:
        print(f"[TTS] gTTS error: {e}")
        return False
    finally:
        # Cleanup temp file
        if temp_file:
            try:
                time.sleep(0.2)
                os.unlink(temp_file)
            except:
                pass


def speak_pyttsx3(text: str, rate: int = 140, volume: float = 1.0, prefer_vi: bool = True) -> bool:
    """
    Speak using pyttsx3 (offline, but poor Vietnamese quality).
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
        print(f"[TTS] pyttsx3 error: {e}")
        return False


def speak(text: str, rate: int = 140, volume: float = 1.0, prefer_vi: bool = True, 
          use_gtts: bool = True, lang: str = "vi") -> bool:
    """
    Speak the given text via system TTS.
    
    Args:
        text: Text to speak
        rate: words per minute (for pyttsx3)
        volume: 0.0 to 1.0
        prefer_vi: try to select Vietnamese voice if available (pyttsx3)
        use_gtts: prefer gTTS over pyttsx3 (better quality)
        lang: Language code for gTTS ('vi' or 'en')

    Returns True if queued successfully.
    """
    if not text:
        return True
    
    # Try gTTS first (better Vietnamese voice)
    if use_gtts and GTTS_AVAILABLE:
        if speak_gtts(text, lang=lang):
            return True
        print("[TTS] gTTS failed, falling back to pyttsx3...")
    
    # Fallback to pyttsx3
    return speak_pyttsx3(text, rate, volume, prefer_vi)

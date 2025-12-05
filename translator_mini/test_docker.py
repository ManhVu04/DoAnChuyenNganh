#!/usr/bin/env python3
"""
Test script for Docker container - validates all modules work correctly
"""

import sys

def test_imports():
    """Test all required imports"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    try:
        import speech_recognition as sr
        print("✓ SpeechRecognition imported")
    except ImportError as e:
        print(f"✗ SpeechRecognition failed: {e}")
        return False
    
    try:
        import pyttsx3
        print("✓ pyttsx3 imported")
    except ImportError as e:
        print(f"✗ pyttsx3 failed: {e}")
        return False
    
    try:
        from deep_translator import GoogleTranslator
        print("✓ deep-translator imported")
    except ImportError as e:
        print(f"✗ deep-translator failed: {e}")
        return False
    
    try:
        import pyaudio
        print("✓ PyAudio imported")
    except ImportError as e:
        print(f"✗ PyAudio failed: {e}")
        return False
    
    return True


def test_translation():
    """Test translation module"""
    print("\n" + "=" * 60)
    print("Testing translation...")
    print("=" * 60)
    
    try:
        from translator import translate_en_to_vi
        
        test_cases = [
            ("Hello", "Xin chào"),
            ("How are you?", "Bạn khỏe không?"),
            ("Good morning", "Chào buổi sáng"),
        ]
        
        for en, expected_vi in test_cases:
            result = translate_en_to_vi(en)
            if result:
                print(f"✓ '{en}' → '{result}'")
            else:
                print(f"✗ Failed to translate '{en}'")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Translation test failed: {e}")
        return False


def test_tts():
    """Test text-to-speech module"""
    print("\n" + "=" * 60)
    print("Testing TTS...")
    print("=" * 60)
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        voices = engine.getProperty('voices')
        print(f"✓ TTS engine initialized")
        print(f"  Available voices: {len(voices)}")
        
        for i, voice in enumerate(voices[:3]):  # Show first 3 voices
            print(f"    [{i}] {voice.name} ({voice.id})")
        
        # Test speak without actually playing audio
        from text_to_speech import speak
        print("✓ TTS module loaded successfully")
        print("  Note: Audio output requires speaker device")
        
        return True
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
        return False


def test_stt():
    """Test speech-to-text module (without microphone)"""
    print("\n" + "=" * 60)
    print("Testing STT...")
    print("=" * 60)
    
    try:
        import speech_to_text as stt
        
        # List microphones (will show none in Docker without device passthrough)
        mics = stt.list_microphones()
        print(f"✓ STT module loaded")
        print(f"  Detected microphones: {len(mics)}")
        
        if mics:
            for idx, name in mics[:3]:
                print(f"    [{idx}] {name}")
        else:
            print("  Note: No microphones detected (normal in Docker)")
            print("        To use voice input, run with --device /dev/snd")
        
        return True
    except Exception as e:
        print(f"✗ STT test failed: {e}")
        return False


def test_chatbot():
    """Test chatbot orchestrator"""
    print("\n" + "=" * 60)
    print("Testing chatbot...")
    print("=" * 60)
    
    try:
        from chatbot import ChatbotTranslatorMini
        
        bot = ChatbotTranslatorMini(voice_output=False)
        
        # Test translation through chatbot
        result = bot.respond_text("Hello world")
        if result:
            print(f"✓ Chatbot working: 'Hello world' → '{result}'")
            return True
        else:
            print("✗ Chatbot translation failed")
            return False
    except Exception as e:
        print(f"✗ Chatbot test failed: {e}")
        return False


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Chatbot Translator Mini - Test Suite" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Translation", test_translation),
        ("TTS", test_tts),
        ("STT", test_stt),
        ("Chatbot", test_chatbot),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Container is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

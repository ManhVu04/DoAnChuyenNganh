"""
Chatbot Translator Mini - Main Entry Point

Modes:
  - voice: Voice input (EN) → Translation → Voice output (VI)
  - text: Text input → Translation → Text/Voice output
  - assistant: AI Voice Assistant (OpenRouter) - bilingual chat
  - assistant-text: AI Text Assistant (OpenRouter) - bilingual chat
"""

import argparse
from typing import Optional

from translator_mini.chatbot import ChatbotTranslatorMini
from translator_mini import speech_to_text as stt


# ==============================================================================
# TRANSLATOR MODES (Original)
# ==============================================================================

def run_voice(mic_index: Optional[int], voice_output: bool, tts_rate: int, loop: bool,
              language_in: str = "en-US"):
    """Voice input translation mode."""
    bot = ChatbotTranslatorMini(voice_output=voice_output, tts_rate=tts_rate, use_gtts=False)

    def one_turn() -> None:
        try:
            text = stt.listen_and_recognize(mic_index=mic_index, language=language_in)
            if not text:
                print("[Main] No recognized text. Try again...")
                return
            
            print(f"[Main] 🎤 Heard: {text}")
            vi = bot.respond_text(text)
            
            if vi is None:
                print("[Main] ❌ Translation failed.")
            else:
                print(f"[Main] 🇻🇳 Vietnamese: {vi}")
                print()  # Empty line for readability
        except Exception as e:
            print(f"[Main] ⚠️ Error in turn: {e}")
            print("[Main] Continuing...")

    if loop:
        print("[Main] 🎙️ Voice mode (continuous loop).")
        print("[Main] Speak English and I'll translate to Vietnamese.")
        print("[Main] Press Ctrl+C to stop.\n")
        try:
            turn_count = 0
            while True:
                turn_count += 1
                print(f"[Main] --- Turn {turn_count} ---")
                one_turn()
                print("[Main] 👂 Listening again...\n")
        except KeyboardInterrupt:
            print("\n[Main] 🛑 Stopped after {turn_count} turns.")
    else:
        print("[Main] Voice mode (single turn).")
        one_turn()


def run_text(voice_output: bool, tts_rate: int, input_text: Optional[str]):
    """Text input translation mode."""
    bot = ChatbotTranslatorMini(voice_output=voice_output, tts_rate=tts_rate, use_gtts=False)

    if input_text is not None:
        vi = bot.respond_text(input_text)
        if vi is None:
            print("[Main] Translation failed.")
        else:
            print(f"[Main] EN: {input_text}")
            print(f"[Main] VI: {vi}")
        return

    print("[Main] Text mode. Type English and press Enter. Ctrl+C to exit.")
    try:
        while True:
            line = input(">> ")
            if not line.strip():
                continue
            vi = bot.respond_text(line)
            if vi is None:
                print("[Main] Translation failed.")
            else:
                print(f"[Main] VI: {vi}")
    except KeyboardInterrupt:
        print("\n[Main] Stopped.")


# ==============================================================================
# AI ASSISTANT MODES (New - OpenRouter)
# ==============================================================================

def run_assistant_voice(
    model: str = "free",
    mic_index: Optional[int] = None,
    use_gtts: bool = True,
    input_language: str = "auto"
):
    """
    AI Voice Assistant mode using OpenRouter.
    Supports bilingual conversation (English + Vietnamese).
    """
    try:
        from translator_mini.voice_assistant import run_voice_assistant
        run_voice_assistant(
            model=model,
            mic_index=mic_index,
            use_gtts=use_gtts,
            input_language=input_language
        )
    except ImportError as e:
        print(f"[Main] Error importing voice_assistant: {e}")
        print("       Make sure openrouter_client.py and voice_assistant.py exist.")


def run_assistant_text(
    model: str = "free",
    use_gtts: bool = True,
    speak_output: bool = True
):
    """
    AI Text Assistant mode using OpenRouter.
    Text input with optional voice output.
    """
    try:
        from translator_mini.voice_assistant import run_text_assistant
        run_text_assistant(
            model=model,
            use_gtts=use_gtts,
            speak_output=speak_output
        )
    except ImportError as e:
        print(f"[Main] Error importing voice_assistant: {e}")
        print("       Make sure openrouter_client.py and voice_assistant.py exist.")


def run_openrouter_chat(model: str = "free"):
    """
    Direct OpenRouter chat (no voice, just API test).
    """
    try:
        from translator_mini.openrouter_client import interactive_chat
        interactive_chat(model=model)
    except ImportError as e:
        print(f"[Main] Error importing openrouter_client: {e}")


# ==============================================================================
# UTILITIES
# ==============================================================================

def list_mics():
    """List available microphones."""
    mics = stt.list_microphones()
    if not mics:
        print("[Main] No microphones detected.")
        return
    print("[Main] Available microphones:")
    for idx, name in mics:
        print(f"  [{idx}] {name}")


def list_models():
    """List available AI models."""
    try:
        from translator_mini.openrouter_client import MODELS
        print("[Main] Available AI models:")
        print("  Free models:")
        for key, value in MODELS.items():
            if "free" in key or ":free" in value:
                print(f"    --model {key:15} → {value}")
        print("  Paid models:")
        for key, value in MODELS.items():
            if "free" not in key and ":free" not in value:
                print(f"    --model {key:15} → {value}")
    except ImportError:
        print("[Main] OpenRouter client not available.")


# ==============================================================================
# ARGUMENT PARSER
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Chatbot Translator Mini - Translation & AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Traditional translator modes
  python -m translator_mini.main --mode voice --loop
  python -m translator_mini.main --mode text --voice-output

  # AI Assistant modes (requires OpenRouter API key)
  python -m translator_mini.main --mode assistant
  python -m translator_mini.main --mode assistant-text --model gpt-4o-mini
  python -m translator_mini.main --mode chat --model claude-sonnet

  # Utilities
  python -m translator_mini.main --list-mics
  python -m translator_mini.main --list-models
        """
    )
    
    # Mode selection
    parser.add_argument(
        "--mode", 
        choices=["voice", "text", "assistant", "assistant-text", "chat"],
        default="voice",
        help="Mode: voice/text (translator), assistant/assistant-text (AI chat), chat (API test)"
    )
    
    # Translator options
    parser.add_argument("--voice-output", action="store_true", 
                        help="Speak Vietnamese output (translator modes)")
    parser.add_argument("--tts-rate", type=int, default=140, 
                        help="TTS speech rate (wpm)")
    parser.add_argument("--loop", action="store_true", 
                        help="Voice mode: continuous loop")
    parser.add_argument("--input", type=str, default=None, 
                        help="Text mode: one-shot input text")
    parser.add_argument("--language-in", type=str, default="en-US", 
                        help="Input speech language (en-US, vi-VN)")
    
    # AI Assistant options
    parser.add_argument("--model", type=str, default="free",
                        help="AI model for assistant modes (free, gpt-4o-mini, claude-sonnet, etc.)")
    parser.add_argument("--gtts", dest="gtts", action="store_true",
                        help="Use Google TTS (default, better voice)")
    parser.add_argument("--no-gtts", dest="gtts", action="store_false",
                        help="Disable Google TTS, use offline pyttsx3")
    parser.set_defaults(gtts=True)
    parser.add_argument("--no-speak", action="store_true",
                        help="Disable voice output in assistant-text mode")
    parser.add_argument("--lang", choices=["auto", "en", "vi"], default="auto",
                        help="Voice input language for assistant mode")
    
    # Microphone options
    parser.add_argument("--mic-index", type=int, default=None, 
                        help="Microphone device index")
    parser.add_argument("--list-mics", action="store_true", 
                        help="List microphone devices and exit")
    
    # Model listing
    parser.add_argument("--list-models", action="store_true",
                        help="List available AI models and exit")
    
    return parser.parse_args()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    args = parse_args()

    # Utility commands
    if args.list_mics:
        list_mics()
    elif args.list_models:
        list_models()
    
    # Mode execution
    elif args.mode == "voice":
        run_voice(
            mic_index=args.mic_index,
            voice_output=args.voice_output,
            tts_rate=args.tts_rate,
            loop=args.loop,
            language_in=args.language_in,
        )
    
    elif args.mode == "text":
        run_text(
            voice_output=args.voice_output,
            tts_rate=args.tts_rate,
            input_text=args.input,
        )
    
    elif args.mode == "assistant":
        run_assistant_voice(
            model=args.model,
            mic_index=args.mic_index,
            use_gtts=args.gtts,
            input_language=args.lang,
        )
    
    elif args.mode == "assistant-text":
        run_assistant_text(
            model=args.model,
            use_gtts=args.gtts,
            speak_output=not args.no_speak,
        )
    
    elif args.mode == "chat":
        run_openrouter_chat(model=args.model)

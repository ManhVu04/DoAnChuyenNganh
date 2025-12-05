import argparse
from typing import Optional

from chatbot import ChatbotTranslatorMini
import speech_to_text as stt


def run_voice(mic_index: Optional[int], voice_output: bool, tts_rate: int, loop: bool,
              language_in: str = "en-US"):
    bot = ChatbotTranslatorMini(voice_output=voice_output, tts_rate=tts_rate)

    def one_turn() -> None:
        text = stt.listen_and_recognize(mic_index=mic_index, language=language_in)
        if not text:
            print("[Main] No recognized text.")
            return
        vi = bot.respond_text(text)
        if vi is None:
            print("[Main] Translation failed.")
        else:
            print(f"[Main] EN: {text}")
            print(f"[Main] VI: {vi}")

    if loop:
        print("[Main] Voice mode (loop). Press Ctrl+C to stop.")
        try:
            while True:
                one_turn()
        except KeyboardInterrupt:
            print("\n[Main] Stopped.")
    else:
        print("[Main] Voice mode (single turn).")
        one_turn()


def run_text(voice_output: bool, tts_rate: int, input_text: Optional[str]):
    bot = ChatbotTranslatorMini(voice_output=voice_output, tts_rate=tts_rate)

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


def list_mics():
    mics = stt.list_microphones()
    if not mics:
        print("[Main] No microphones detected.")
        return
    print("[Main] Available microphones:")
    for idx, name in mics:
        print(f"  [{idx}] {name}")


def parse_args():
    parser = argparse.ArgumentParser(description="Chatbot Translator Mini (EN -> VI)")
    parser.add_argument("--mode", choices=["voice", "text"], default="voice",
                        help="Run in voice (mic) or text (keyboard) mode")
    parser.add_argument("--voice-output", action="store_true", help="Speak Vietnamese output")
    parser.add_argument("--tts-rate", type=int, default=160, help="TTS speech rate (wpm)")
    parser.add_argument("--mic-index", type=int, default=None, help="Microphone device index")
    parser.add_argument("--list-mics", action="store_true", help="List microphone devices and exit")
    parser.add_argument("--loop", action="store_true", help="Voice mode: continuous loop")
    parser.add_argument("--input", type=str, default=None, help="Text mode: one-shot input text (English)")
    parser.add_argument("--language-in", type=str, default="en-US", help="Input speech language code")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.list_mics:
        list_mics()
    else:
        if args.mode == "voice":
            run_voice(
                mic_index=args.mic_index,
                voice_output=args.voice_output,
                tts_rate=args.tts_rate,
                loop=args.loop,
                language_in=args.language_in,
            )
        else:
            run_text(
                voice_output=args.voice_output,
                tts_rate=args.tts_rate,
                input_text=args.input,
            )

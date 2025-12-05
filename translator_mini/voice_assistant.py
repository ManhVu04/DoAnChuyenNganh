"""
Voice Assistant for Chatbot Translator Mini
Combines voice input (EN/VI), AI chat (OpenRouter), and voice output.
"""

import sys
import re
from typing import Optional, Tuple

# Import local modules
from translator_mini.speech_to_text import listen_and_recognize, list_microphones
from translator_mini.text_to_speech import speak
from translator_mini.openrouter_client import (
    OpenRouterChatbot,
    get_api_key,
    translate_en_to_vi,
    translate_vi_to_en,
    MODELS
)


# ==============================================================================
# LANGUAGE DETECTION
# ==============================================================================

def detect_language(text: str) -> str:
    """
    Detect if text is Vietnamese or English.
    Returns: "vi" or "en"
    """
    # Vietnamese characters (diacritics)
    vi_pattern = r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]'
    
    # Count Vietnamese characters
    vi_chars = len(re.findall(vi_pattern, text.lower()))
    
    # If more than 5% Vietnamese characters, it's likely Vietnamese
    if len(text) > 0 and vi_chars / len(text) > 0.05:
        return "vi"
    
    # Common Vietnamese words
    vi_words = [
        'xin', 'chào', 'cảm', 'ơn', 'không', 'có', 'là', 'của', 'và', 'được',
        'này', 'đó', 'để', 'cho', 'với', 'trong', 'như', 'nhưng', 'thì', 'mà',
        'bạn', 'tôi', 'anh', 'chị', 'em', 'ông', 'bà', 'nó', 'họ', 'chúng',
        'làm', 'muốn', 'biết', 'nói', 'giúp', 'hỏi', 'trả', 'lời', 'dịch'
    ]
    
    words = text.lower().split()
    vi_word_count = sum(1 for w in words if w in vi_words)
    
    if len(words) > 0 and vi_word_count / len(words) > 0.2:
        return "vi"
    
    return "en"


# ==============================================================================
# VOICE ASSISTANT CLASS
# ==============================================================================

class VoiceAssistant:
    """
    Voice-enabled AI Assistant with bilingual support (EN/VI).
    
    Features:
    - Voice input (English and Vietnamese)
    - AI chat using OpenRouter (GPT-4, Claude, Llama, etc.)
    - Voice output (TTS)
    - Auto language detection
    """
    
    def __init__(
        self,
        model: str = "free",
        api_key: Optional[str] = None,
        mic_index: Optional[int] = None,
        use_gtts: bool = True,  # True = Google TTS (giọng hay), False = pyttsx3 (offline)
        voice_rate: int = 150,
        input_language: str = "auto",  # "auto", "en", "vi"
    ):
        """
        Initialize Voice Assistant.
        
        Args:
            model: OpenRouter model name/alias
            api_key: API key (or uses api_key.txt)
            mic_index: Microphone index (None for default)
            use_gtts: Use Google TTS (True) or pyttsx3 (False)
            voice_rate: Speech rate for pyttsx3
            input_language: Voice input language ("auto", "en", "vi")
        """
        self.model = model
        self.mic_index = mic_index
        self.use_gtts = use_gtts
        self.voice_rate = voice_rate
        self.input_language = input_language
        
        # Initialize chatbot
        self.chatbot = OpenRouterChatbot(
            model=model,
            api_key=api_key,
            system_prompt=(
                "Bạn là trợ lý giọng nói AI thông minh tên là Mini, nói tiếng Việt. "
                "Trả lời ngắn gọn và tự nhiên như đang nói chuyện. "
                "QUAN TRỌNG: Khi người dùng nói 'dịch' hoặc 'translate' kèm theo một câu tiếng Anh, "
                "hãy dịch câu đó sang tiếng Việt. Ví dụ: 'dịch I love you' → 'Tôi yêu bạn'. "
                "Chỉ trả về bản dịch, không giải thích thêm. "
                "Nếu không phải yêu cầu dịch, hãy trả lời bằng tiếng Việt."
            )
        )
        
        print(f"[VoiceAssistant] Initialized with model: {MODELS.get(model, model)}")
    
    def listen(self, prompt: str = "🎤 Đang nghe... (Listening...)") -> Optional[str]:
        """
        Listen for voice input.
        
        Returns:
            Recognized text or None
        """
        print(prompt)
        
        # Determine language code for recognition
        if self.input_language == "vi":
            lang_code = "vi-VN"
        elif self.input_language == "en":
            lang_code = "en-US"
        else:
            # Auto: try Vietnamese first (default), then English
            lang_code = "vi-VN"
        
        text = listen_and_recognize(
            mic_index=self.mic_index,
            language=lang_code,
            timeout=8.0,
            phrase_time_limit=15.0
        )
        
        # If auto mode and got nothing, try English
        if text is None and self.input_language == "auto":
            print("   → Thử nhận dạng tiếng Anh...")
            text = listen_and_recognize(
                mic_index=self.mic_index,
                language="en-US",
                timeout=5.0,
                phrase_time_limit=15.0
            )
        
        return text
    
    def think(self, user_input: str) -> Optional[str]:
        """
        Process user input and get AI response.
        
        Args:
            user_input: Text from user (voice or typed)
        
        Returns:
            AI response text
        """
        print(f"💭 Đang suy nghĩ... (Thinking...)")
        
        response = self.chatbot.chat(user_input)
        
        if response:
            print(f"🤖 AI: {response}")
        else:
            print("❌ Không nhận được phản hồi từ AI")
        
        return response
    
    def speak_response(self, text: str, language: str = "auto") -> None:
        """
        Speak the response using TTS.
        
        Args:
            text: Text to speak
            language: "vi", "en", or "auto" (detect)
        """
        import sys
        import time
        
        if language == "auto":
            language = detect_language(text)
        
        print(f"🔊 Đang phát âm thanh... ({language})")
        sys.stdout.flush()
        
        # Small delay to ensure audio device is ready
        time.sleep(0.1)
        
        success = speak(
            text=text,
            lang=language,
            use_gtts=self.use_gtts,
            rate=self.voice_rate
        )
        
        if success:
            print("✅ Đã phát âm thanh xong.")
        else:
            print("⚠️ Không thể phát âm thanh. Kiểm tra loa/tai nghe.")
        sys.stdout.flush()
    
    def process_turn(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process one conversation turn: listen → think → speak.
        
        Returns:
            (continue_loop, user_input, ai_response)
        """
        # Listen
        user_input = self.listen()
        
        if user_input is None:
            print("   → Không nghe thấy gì. Thử lại...")
            return True, None, None
        
        print(f"👤 Bạn: {user_input}")
        
        # Check for exit commands
        exit_commands = ["quit", "exit", "bye", "goodbye", "thoát", "tạm biệt", "kết thúc", "dừng lại"]
        if user_input.lower().strip() in exit_commands:
            print("👋 Tạm biệt! Goodbye!")
            self.speak_response("Tạm biệt! Hẹn gặp lại! Goodbye!")
            return False, user_input, None
        
        # Think
        response = self.think(user_input)
        
        if response:
            # Speak response
            self.speak_response(response)
        
        return True, user_input, response
    
    def run(self) -> None:
        """
        Run the voice assistant in a loop.
        """
        print("\n" + "=" * 60)
        print("🎙️  VOICE ASSISTANT - MINI")
        print(f"   Model: {MODELS.get(self.model, self.model)}")
        print("   Nói 'thoát' hoặc 'quit' để kết thúc")
        print("   💡 Nói 'dịch [câu tiếng Anh]' để dịch sang tiếng Việt")
        print("=" * 60 + "\n")
        
        # Greeting
        greeting = "Xin chào! Tôi là Mini, trợ lý AI của bạn. Bạn có thể hỏi tôi bất cứ điều gì, hoặc nói 'dịch' kèm câu tiếng Anh để tôi dịch sang tiếng Việt."
        print(f"🤖 AI: {greeting}")
        self.speak_response(greeting, language="vi")
        
        # Main loop
        while True:
            try:
                print("\n" + "-" * 40)
                continue_loop, _, _ = self.process_turn()
                
                if not continue_loop:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Đã dừng bởi người dùng. Tạm biệt!")
                break
    
    def reset(self) -> None:
        """Reset conversation history."""
        self.chatbot.reset()
        print("🔄 Đã reset cuộc hội thoại.")


# ==============================================================================
# TEXT ASSISTANT (for testing without microphone)
# ==============================================================================

class TextAssistant:
    """
    Text-based AI Assistant (no voice input, optional voice output).
    """
    
    def __init__(
        self,
        model: str = "free",
        api_key: Optional[str] = None,
        use_gtts: bool = True,  # True = Google TTS (giọng hay), False = pyttsx3
        voice_rate: int = 150,
        speak_output: bool = True,
    ):
        self.model = model
        self.use_gtts = use_gtts
        self.voice_rate = voice_rate
        self.speak_output = speak_output
        
        self.chatbot = OpenRouterChatbot(
            model=model,
            api_key=api_key,
            system_prompt=(
                "Bạn là trợ lý AI thông minh tên là Mini, nói tiếng Việt. "
                "Trả lời ngắn gọn và tự nhiên. "
                "QUAN TRỌNG: Khi người dùng nói 'dịch' hoặc 'translate' kèm theo một câu tiếng Anh, "
                "hãy dịch câu đó sang tiếng Việt. Ví dụ: 'dịch I love you' → 'Tôi yêu bạn'. "
                "Chỉ trả về bản dịch, không giải thích thêm. "
                "Nếu không phải yêu cầu dịch, hãy trả lời bằng tiếng Việt."
            )
        )
    
    def chat(self, user_input: str) -> Optional[str]:
        """Process text input and return/speak response."""
        response = self.chatbot.chat(user_input)
        
        if response and self.speak_output:
            lang = detect_language(response)
            print(f"🔊 Đang phát âm thanh... ({lang})")
            success = speak(text=response, lang=lang, use_gtts=self.use_gtts, rate=self.voice_rate)
            if success:
                print("✅ Đã phát âm thanh xong.")
            else:
                print("⚠️ Không thể phát âm thanh.")
        
        return response
    
    def run(self) -> None:
        """Run interactive text chat."""
        print("\n" + "=" * 60)
        print("💬 TEXT ASSISTANT - MINI")
        print(f"   Model: {MODELS.get(self.model, self.model)}")
        print("   Gõ 'quit' để thoát, 'reset' để xóa lịch sử")
        print("   Gõ 'voice on/off' để bật/tắt giọng nói")
        print("   💡 Gõ 'dịch [câu tiếng Anh]' để dịch sang tiếng Việt")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("👤 Bạn: ").strip()
                
                if not user_input:
                    continue
                
                # Commands
                if user_input.lower() in ["quit", "exit", "thoát"]:
                    print("👋 Tạm biệt!")
                    break
                
                if user_input.lower() == "reset":
                    self.chatbot.reset()
                    print("🔄 Đã reset cuộc hội thoại.")
                    continue
                
                if user_input.lower() == "voice on":
                    self.speak_output = True
                    print("🔊 Đã bật giọng nói.")
                    continue
                
                if user_input.lower() == "voice off":
                    self.speak_output = False
                    print("🔇 Đã tắt giọng nói.")
                    continue
                
                # Get response
                print("💭 Đang suy nghĩ...")
                response = self.chat(user_input)
                
                if response:
                    print(f"🤖 AI: {response}")
                else:
                    print("❌ Không nhận được phản hồi.")
                    
            except KeyboardInterrupt:
                print("\n👋 Tạm biệt!")
                break


# ==============================================================================
# STANDALONE FUNCTIONS
# ==============================================================================

def run_voice_assistant(
    model: str = "free",
    mic_index: Optional[int] = None,
    use_gtts: bool = False,
    input_language: str = "auto"
) -> None:
    """Run voice assistant with specified settings."""
    if not get_api_key():
        print("❌ Không tìm thấy API key!")
        print("   1. Lấy key tại: https://openrouter.ai/keys")
        print("   2. Tạo file api_key.txt chứa key")
        return
    
    assistant = VoiceAssistant(
        model=model,
        mic_index=mic_index,
        use_gtts=use_gtts,
        input_language=input_language
    )
    assistant.run()


def run_text_assistant(
    model: str = "free",
    use_gtts: bool = False,
    speak_output: bool = True
) -> None:
    """Run text assistant with optional voice output."""
    if not get_api_key():
        print("❌ Không tìm thấy API key!")
        print("   1. Lấy key tại: https://openrouter.ai/keys")
        print("   2. Tạo file api_key.txt chứa key")
        return
    
    assistant = TextAssistant(
        model=model,
        use_gtts=use_gtts,
        speak_output=speak_output
    )
    assistant.run()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice/Text AI Assistant")
    parser.add_argument("--mode", choices=["voice", "text"], default="text",
                        help="Assistant mode: voice (with microphone) or text (keyboard)")
    parser.add_argument("--model", default="free",
                        help="AI model to use (free, gpt-4o-mini, claude-sonnet, etc.)")
    parser.add_argument("--gtts", action="store_true",
                        help="Use Google TTS instead of pyttsx3")
    parser.add_argument("--lang", choices=["auto", "en", "vi"], default="auto",
                        help="Voice input language")
    parser.add_argument("--no-voice", action="store_true",
                        help="Disable voice output (text mode only)")
    parser.add_argument("--list-mics", action="store_true",
                        help="List available microphones and exit")
    parser.add_argument("--mic", type=int, default=None,
                        help="Microphone index to use")
    
    args = parser.parse_args()
    
    if args.list_mics:
        print("🎤 Available microphones:")
        for idx, name in list_microphones():
            print(f"   [{idx}] {name}")
        sys.exit(0)
    
    if args.mode == "voice":
        run_voice_assistant(
            model=args.model,
            mic_index=args.mic,
            use_gtts=args.gtts,
            input_language=args.lang
        )
    else:
        run_text_assistant(
            model=args.model,
            use_gtts=args.gtts,
            speak_output=not args.no_voice
        )

"""
Google Gemini API Client (direct, no OpenRouter)
Provides a Chatbot class compatible with OpenRouterChatbot interface.
"""

import os
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
except ImportError as exc:  # pragma: no cover
    raise ImportError("google-generativeai is required for Gemini client. Install with `pip install google-generativeai`." ) from exc

# Model aliases - verified available models from API
MODELS = {
    "gemini-flash": "gemini-flash-latest",           # Alias tự động → model flash mới nhất (free)
    "gemini-pro": "gemini-pro-latest",               # Alias tự động → model pro mới nhất (free)
    # Gemini 2.0 (free tier)
    "gemini-2-flash": "gemini-2.0-flash",            # Ổn định
    "gemini-2-flash-lite": "gemini-2.0-flash-lite",  # Nhẹ, nhanh hơn
    # Gemini 2.5 (free tier)
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
}


def get_api_key(key_file: str = "gemini_api_key.txt") -> Optional[str]:
    """Get Gemini API key from file or env (GEMINI_API_KEY)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(script_dir, key_file)

    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key and not key.startswith("#"):
                return key

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key.strip()

    return None


def _configure_client(api_key: str) -> None:
    """Configure global Gemini client."""
    genai.configure(api_key=api_key)


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-flash-latest",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> Optional[str]:
    """Send chat completion request to Gemini.

    Args:
        messages: list of {role, content}
        model: model id or alias
        api_key: Gemini API key (file/env fallback)
    Returns: response text or None
    """
    key = api_key or get_api_key()
    if not key:
        print("[Gemini] ERROR: No GEMINI_API_KEY or gemini_api_key.txt found")
        return None

    _configure_client(key)

    model_id = MODELS.get(model, model)

    # Flatten OpenAI-style messages to a single prompt for Gemini
    prompt_lines = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        role_tag = "User" if role == "user" else ("Assistant" if role == "assistant" else "System")
        prompt_lines.append(f"{role_tag}: {content}")
    prompt_lines.append("Assistant:")
    prompt = "\n".join(prompt_lines)

    try:
        model_obj = genai.GenerativeModel(model_id)
        resp = model_obj.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        text = resp.text if resp and hasattr(resp, "text") else None
        return text.strip() if text else None
    except Exception as e:  # broad to keep simple for runtime issues
        print(f"[Gemini] Request error: {e}")
        return None


class GeminiChatbot:
    """Stateful chatbot compatible with OpenRouterChatbot interface."""

    def __init__(
        self,
        model: str = "gemini-flash-latest",
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_history: int = 20,
    ):
        self.model = model
        self.api_key = api_key or get_api_key()
        self.max_history = max_history
        self.system_prompt = system_prompt or (
            "Bạn là trợ lý AI thông minh, có thể nói tiếng Việt và tiếng Anh. "
            "Trả lời ngắn gọn, rõ ràng và hữu ích."
        )
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, user_message: str) -> Optional[str]:
        temp_messages = self.messages + [{"role": "user", "content": user_message}]
        response = chat_completion(
            messages=temp_messages,
            model=self.model,
            api_key=self.api_key,
        )
        if response:
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": response})
            if len(self.messages) > self.max_history + 1:
                self.messages = [self.messages[0]] + self.messages[-self.max_history:]
        return response

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt = prompt
        self.reset()


def interactive_chat(model: str = "gemini-flash-latest"):
    """Simple interactive CLI chat with Gemini (no voice)."""
    print("=" * 60)
    print("🤖 Gemini Chat")
    print(f"   Model: {MODELS.get(model, model)}")
    print("   Type 'quit' to exit, 'reset' to clear history")
    print("=" * 60)

    bot = GeminiChatbot(model=model)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Bye!")
                break
            if user_input.lower() == "reset":
                bot.reset()
                print("🔄 History cleared.")
                continue

            resp = bot.chat(user_input)
            if resp:
                print(f"🤖 AI: {resp}")
            else:
                print("⚠️ No response.")
        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break

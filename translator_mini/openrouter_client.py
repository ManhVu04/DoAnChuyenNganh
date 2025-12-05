"""
OpenRouter API Client for Chatbot Translator Mini
Supports multiple AI models (GPT-4, Claude, Llama, Gemini, etc.)
"""

import os
import json
import requests
from typing import Optional, Generator, Dict, Any, List

# ==============================================================================
# AVAILABLE MODELS (OpenRouter.ai)
# ==============================================================================
MODELS = {
    # Free models (có giới hạn rate)
    "free": "meta-llama/llama-3.2-3b-instruct:free",
    "llama-free": "meta-llama/llama-3.2-3b-instruct:free",
    "gemma-free": "google/gemma-2-9b-it:free",
    "qwen-free": "qwen/qwen-2-7b-instruct:free",
    
    # Paid models (giá rẻ và chất lượng tốt)
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    "claude-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-haiku": "anthropic/claude-3-haiku",
    "llama-70b": "meta-llama/llama-3.1-70b-instruct",
    "gemini-flash": "google/gemini-flash-1.5",
    "gemini-pro": "google/gemini-pro-1.5",
    "deepseek": "deepseek/deepseek-chat",
    "mistral": "mistralai/mistral-7b-instruct",
}

API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==============================================================================
# API KEY MANAGEMENT
# ==============================================================================

def get_api_key(key_file: str = "api_key.txt") -> Optional[str]:
    """
    Get API key from file or environment variable.
    Priority: api_key.txt > OPENROUTER_API_KEY env var
    """
    # Try file first
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(script_dir, key_file)
    
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key and not key.startswith("#"):
                return key
    
    # Try environment variable
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        return env_key
    
    return None


def set_api_key(api_key: str, key_file: str = "api_key.txt") -> None:
    """Save API key to file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(script_dir, key_file)
    
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(api_key)
    print(f"[OpenRouter] API key saved to {key_path}")


# ==============================================================================
# CORE API FUNCTIONS
# ==============================================================================

def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "free",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    site_url: str = "http://localhost:3000",
    site_name: str = "Chatbot Translator Mini"
) -> Optional[str]:
    """
    Send chat completion request to OpenRouter API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name or alias from MODELS dict
        api_key: API key (will use get_api_key() if not provided)
        temperature: Creativity (0.0-2.0)
        max_tokens: Max response length
        site_url: Your app URL (for OpenRouter tracking)
        site_name: Your app name
    
    Returns:
        Response text or None on error
    """
    # Get API key
    key = api_key or get_api_key()
    if not key:
        print("[OpenRouter] ERROR: No API key found!")
        print("  → Create api_key.txt with your key, or set OPENROUTER_API_KEY env var")
        return None
    
    # Resolve model alias
    model_id = MODELS.get(model, model)
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
    }
    
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if "error" in data:
            print(f"[OpenRouter] API Error: {data['error']}")
            return None
        
        # Extract response text
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()
        
    except requests.exceptions.Timeout:
        print("[OpenRouter] Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[OpenRouter] Request error: {e}")
        return None
    except json.JSONDecodeError:
        print("[OpenRouter] Invalid JSON response")
        return None


def chat_completion_stream(
    messages: List[Dict[str, str]],
    model: str = "free",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> Generator[str, None, None]:
    """
    Stream chat completion response (for real-time output).
    
    Yields:
        Text chunks as they arrive
    """
    key = api_key or get_api_key()
    if not key:
        print("[OpenRouter] ERROR: No API key found!")
        return
    
    model_id = MODELS.get(model, model)
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    
    try:
        with requests.post(API_BASE_URL, headers=headers, json=payload, 
                          stream=True, timeout=60) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
    except requests.exceptions.RequestException as e:
        print(f"[OpenRouter] Stream error: {e}")


# ==============================================================================
# TRANSLATION FUNCTIONS
# ==============================================================================

def translate_en_to_vi(
    text: str,
    model: str = "free",
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Translate English to Vietnamese using AI.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là một dịch giả chuyên nghiệp Anh-Việt. "
                "Chỉ trả về bản dịch tiếng Việt, không giải thích thêm."
            )
        },
        {
            "role": "user",
            "content": f"Dịch sang tiếng Việt: {text}"
        }
    ]
    
    return chat_completion(messages, model=model, api_key=api_key, temperature=0.3)


def translate_vi_to_en(
    text: str,
    model: str = "free",
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Translate Vietnamese to English using AI.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional Vietnamese-English translator. "
                "Only return the English translation, no explanations."
            )
        },
        {
            "role": "user",
            "content": f"Translate to English: {text}"
        }
    ]
    
    return chat_completion(messages, model=model, api_key=api_key, temperature=0.3)


def translate_auto(
    text: str,
    model: str = "free",
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Auto-detect language and translate:
    - English → Vietnamese
    - Vietnamese → English
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a bilingual translator. "
                "If the input is English, translate to Vietnamese. "
                "If the input is Vietnamese, translate to English. "
                "Only return the translation, no explanations."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]
    
    return chat_completion(messages, model=model, api_key=api_key, temperature=0.3)


# ==============================================================================
# CHATBOT CLASS
# ==============================================================================

class OpenRouterChatbot:
    """
    A conversational chatbot using OpenRouter API with conversation history.
    """
    
    def __init__(
        self,
        model: str = "free",
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_history: int = 20
    ):
        self.model = model
        self.api_key = api_key or get_api_key()
        self.max_history = max_history
        
        # Default system prompt (bilingual assistant)
        self.system_prompt = system_prompt or (
            "Bạn là trợ lý AI thông minh, có thể nói tiếng Việt và tiếng Anh. "
            "You are a smart AI assistant that can speak both Vietnamese and English. "
            "Trả lời bằng ngôn ngữ mà người dùng sử dụng. "
            "Reply in the same language the user uses. "
            "Trả lời ngắn gọn, rõ ràng và hữu ích."
        )
        
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def chat(self, user_message: str) -> Optional[str]:
        """
        Send a message and get a response.
        Maintains conversation history.
        Only saves to history if request succeeds.
        """
        # Temporarily add user message for the request
        temp_messages = self.messages + [{"role": "user", "content": user_message}]
        
        # Get response
        response = chat_completion(
            messages=temp_messages,
            model=self.model,
            api_key=self.api_key
        )
        
        if response:
            # Only save to history if successful
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": response})
            
            # Trim history if too long (keep system + recent messages)
            if len(self.messages) > self.max_history + 1:
                self.messages = [self.messages[0]] + self.messages[-(self.max_history):]
        
        return response
    
    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Send a message and stream the response.
        """
        # Temporarily add for streaming
        temp_messages = self.messages + [{"role": "user", "content": user_message}]
        
        full_response = []
        for chunk in chat_completion_stream(
            messages=temp_messages,
            model=self.model,
            api_key=self.api_key
        ):
            full_response.append(chunk)
            yield chunk
        
        # Only add to history if we got a response
        if full_response:
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": "".join(full_response)})
    
    def reset(self) -> None:
        """Reset conversation history."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
    
    def set_system_prompt(self, prompt: str) -> None:
        """Change system prompt and reset conversation."""
        self.system_prompt = prompt
        self.reset()


# ==============================================================================
# INTERACTIVE CHAT (for testing)
# ==============================================================================

def interactive_chat(model: str = "free"):
    """
    Run interactive chat in terminal.
    """
    print("=" * 60)
    print("🤖 OpenRouter AI Chat")
    print(f"   Model: {MODELS.get(model, model)}")
    print("   Type 'quit' to exit, 'reset' to clear history")
    print("=" * 60)
    
    bot = OpenRouterChatbot(model=model)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "bye", "thoát"]:
                print("👋 Goodbye! Tạm biệt!")
                break
            
            if user_input.lower() == "reset":
                bot.reset()
                print("🔄 Conversation reset.")
                continue
            
            print("🤖 AI: ", end="", flush=True)
            
            # Stream response
            for chunk in bot.chat_stream(user_input):
                print(chunk, end="", flush=True)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


# ==============================================================================
# MAIN (for testing)
# ==============================================================================

if __name__ == "__main__":
    import sys
    
    # Check API key
    if not get_api_key():
        print("⚠️  No API key found!")
        print("   1. Get your key at: https://openrouter.ai/keys")
        print("   2. Create api_key.txt with your key")
        print("   OR set OPENROUTER_API_KEY environment variable")
        sys.exit(1)
    
    # Parse model from args
    model = "free"
    if len(sys.argv) > 1:
        model = sys.argv[1]
    
    # Run interactive chat
    interactive_chat(model=model)

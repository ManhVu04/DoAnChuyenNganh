# OpenRouter AI Setup Guide

## 🚀 Bắt đầu nhanh | Quick Start

### 1. Lấy API Key | Get API Key

1. Truy cập: **https://openrouter.ai/keys**
2. Đăng nhập bằng Google/GitHub
3. Tạo API key mới
4. Copy key (dạng `sk-or-v1-xxxx...`)

### 2. Cấu hình API Key | Configure API Key

**Cách 1:** Tạo file `api_key.txt`:
```bash
cd translator_mini
echo "sk-or-v1-your-key-here" > api_key.txt
```

**Cách 2:** Đặt biến môi trường:
```bash
# Windows PowerShell
$env:OPENROUTER_API_KEY = "sk-or-v1-your-key-here"

# Linux/Mac
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

### 3. Chạy thử | Test

```bash
# Text chat (không cần mic)
python -m translator_mini.main --mode assistant-text

# Voice assistant (cần mic)
python -m translator_mini.main --mode assistant
```

---

## 📋 Các model có sẵn | Available Models

### Free Models (Miễn phí)
| Alias | Model | Ghi chú |
|-------|-------|---------|
| `free` | meta-llama/llama-3.2-3b-instruct:free | Mặc định, tốc độ nhanh |
| `llama-free` | meta-llama/llama-3.2-3b-instruct:free | Giống `free` |
| `gemma-free` | google/gemma-2-9b-it:free | Google Gemma |
| `qwen-free` | qwen/qwen-2-7b-instruct:free | Alibaba Qwen |

### Paid Models (Trả phí - giá rẻ)
| Alias | Model | Chi phí ước tính |
|-------|-------|------------------|
| `gpt-4o-mini` | openai/gpt-4o-mini | ~$0.15/1M tokens |
| `gpt-4o` | openai/gpt-4o | ~$5/1M tokens |
| `claude-sonnet` | anthropic/claude-3.5-sonnet | ~$3/1M tokens |
| `claude-haiku` | anthropic/claude-3-haiku | ~$0.25/1M tokens |
| `gemini-flash` | google/gemini-flash-1.5 | ~$0.075/1M tokens |
| `deepseek` | deepseek/deepseek-chat | ~$0.14/1M tokens |

**Sử dụng model:**
```bash
python -m translator_mini.main --mode assistant-text --model gpt-4o-mini
python -m translator_mini.main --mode assistant --model claude-sonnet
```

---

## 💡 Ví dụ sử dụng | Usage Examples

### Chat văn bản | Text Chat
```bash
# Chat cơ bản
python -m translator_mini.main --mode chat

# Chat với model tốt hơn
python -m translator_mini.main --mode chat --model gpt-4o-mini

# Assistant có giọng nói output
python -m translator_mini.main --mode assistant-text

# Tắt giọng nói
python -m translator_mini.main --mode assistant-text --no-speak
```

### Voice Assistant (cần microphone)
```bash
# Mặc định (auto detect ngôn ngữ)
python -m translator_mini.main --mode assistant

# Chỉ định ngôn ngữ input
python -m translator_mini.main --mode assistant --lang vi
python -m translator_mini.main --mode assistant --lang en

# Dùng Google TTS (giọng hay hơn)
python -m translator_mini.main --mode assistant --gtts

# Chọn microphone
python -m translator_mini.main --list-mics
python -m translator_mini.main --mode assistant --mic-index 1
```

---

## 🔧 Troubleshooting

### "No API key found"
- Kiểm tra file `api_key.txt` tồn tại
- Key không có dấu cách thừa
- Key bắt đầu bằng `sk-or-`

### "API Error: insufficient_quota"
- Tài khoản hết credit
- Thêm credit tại: https://openrouter.ai/credits
- Hoặc dùng model free: `--model free`

### "Request timed out"
- Kiểm tra kết nối internet
- Thử lại sau vài giây
- Model free có thể chậm hơn

---

## 📚 API Reference

### Python Code
```python
from translator_mini.openrouter_client import (
    OpenRouterChatbot,
    chat_completion,
    translate_en_to_vi,
    translate_vi_to_en
)

# Simple chat
response = chat_completion([
    {"role": "user", "content": "Xin chào!"}
], model="free")
print(response)

# Translation
vi = translate_en_to_vi("Hello, how are you?")
print(vi)  # "Xin chào, bạn khỏe không?"

en = translate_vi_to_en("Tôi đang học tiếng Anh")
print(en)  # "I am learning English"

# Chatbot with history
bot = OpenRouterChatbot(model="gpt-4o-mini")
print(bot.chat("Hello!"))
print(bot.chat("What did I just say?"))  # Remembers context
```

### Voice Assistant
```python
from translator_mini.voice_assistant import VoiceAssistant

assistant = VoiceAssistant(
    model="gpt-4o-mini",
    use_gtts=True,
    input_language="auto"
)
assistant.run()  # Starts voice loop
```

---

## 💰 Chi phí ước tính | Cost Estimation

- 1 cuộc hội thoại ~10 lượt = ~2000 tokens
- Model `gpt-4o-mini`: ~$0.0003/cuộc hội thoại
- Model `free`: $0 (có rate limit)

**Tip:** Bắt đầu với model `free` để test, sau đó upgrade lên `gpt-4o-mini` hoặc `claude-haiku` để có trải nghiệm tốt hơn.

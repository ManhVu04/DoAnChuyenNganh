# 🎙️ Voice Assistant Guide - Mini AI

## Tổng quan | Overview

Voice Assistant "Mini" là trợ lý AI song ngữ (Việt-Anh) với khả năng:
- 🎤 Nhận giọng nói tiếng Việt và tiếng Anh
- 🤖 Trò chuyện như ChatGPT (sử dụng OpenRouter API)
- 🔊 Phản hồi bằng giọng nói

---

## 🚀 Khởi động nhanh | Quick Start

### Bước 1: Cài đặt dependencies
```bash
cd translator_mini
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Key
1. Lấy key tại: https://openrouter.ai/keys
2. Tạo file `api_key.txt`:
```bash
echo "sk-or-v1-your-key-here" > api_key.txt
```

### Bước 3: Chạy Assistant

**Text mode (không cần microphone):**
```bash
python -m translator_mini.main --mode assistant-text
```

**Voice mode (cần microphone):**
```bash
python -m translator_mini.main --mode assistant
```

---

## 📖 Các chế độ | Modes

### 1. `assistant` - Voice Assistant
Nói chuyện bằng giọng nói, AI phản hồi bằng giọng nói.

```bash
python -m translator_mini.main --mode assistant
```

**Tùy chọn:**
- `--lang auto` - Tự động nhận dạng EN/VI (mặc định)
- `--lang en` - Chỉ nhận tiếng Anh
- `--lang vi` - Chỉ nhận tiếng Việt
- `--gtts` - Dùng Google TTS (giọng hay hơn, cần internet)
- `--mic-index N` - Chọn microphone

**Ví dụ:**
```bash
# Giọng hay hơn với Google TTS
python -m translator_mini.main --mode assistant --gtts

# Chỉ nói tiếng Việt
python -m translator_mini.main --mode assistant --lang vi

# Chọn microphone index 2
python -m translator_mini.main --mode assistant --mic-index 2
```

### 2. `assistant-text` - Text Assistant
Gõ bàn phím, AI phản hồi bằng giọng nói (hoặc text).

```bash
python -m translator_mini.main --mode assistant-text
```

**Tùy chọn:**
- `--no-speak` - Tắt giọng nói, chỉ hiển thị text
- `--gtts` - Dùng Google TTS

**Commands trong chat:**
- `quit` / `thoát` - Thoát
- `reset` - Xóa lịch sử hội thoại
- `voice on` - Bật giọng nói
- `voice off` - Tắt giọng nói

### 3. `chat` - API Test
Chat trực tiếp với OpenRouter API (không voice).

```bash
python -m translator_mini.main --mode chat
python -m translator_mini.main --mode chat --model gpt-4o-mini
```

---

## 🎯 Ví dụ hội thoại | Example Conversations

### Tiếng Việt
```
👤 Bạn: Xin chào, bạn là ai?
🤖 AI: Xin chào! Tôi là Mini, trợ lý AI của bạn. Tôi có thể giúp gì cho bạn hôm nay?

👤 Bạn: Thời tiết hôm nay thế nào?
🤖 AI: Tôi không có khả năng kiểm tra thời tiết thực tế, nhưng bạn có thể...
```

### Tiếng Anh
```
👤 You: Hello, what can you do?
🤖 AI: Hello! I'm Mini, your AI assistant. I can help with...

👤 You: Translate "I love Vietnam" to Vietnamese
🤖 AI: "Tôi yêu Việt Nam"
```

### Song ngữ | Bilingual
```
👤 Bạn: Can you explain machine learning bằng tiếng Việt?
🤖 AI: Chắc chắn rồi! Machine learning (học máy) là một nhánh...
```

---

## 🤖 Chọn model AI | Choose AI Model

### Xem danh sách model
```bash
python -m translator_mini.main --list-models
```

### Sử dụng model cụ thể
```bash
# Free (mặc định)
python -m translator_mini.main --mode assistant --model free

# GPT-4o Mini (rẻ, chất lượng tốt)
python -m translator_mini.main --mode assistant --model gpt-4o-mini

# Claude Sonnet (thông minh nhất)
python -m translator_mini.main --mode assistant --model claude-sonnet

# Gemini Flash (nhanh)
python -m translator_mini.main --mode assistant --model gemini-flash
```

**Khuyến nghị:**
- Test: `free`
- Daily use: `gpt-4o-mini` hoặc `claude-haiku`
- Complex tasks: `claude-sonnet` hoặc `gpt-4o`

---

## 🎤 Cấu hình Microphone

### Xem danh sách microphone
```bash
python -m translator_mini.main --list-mics
```

Output:
```
[Main] Available microphones:
  [0] Microsoft Sound Mapper - Input
  [1] Microphone (Realtek Audio)
  [2] Headset Microphone
```

### Chọn microphone
```bash
python -m translator_mini.main --mode assistant --mic-index 1
```

---

## 🔊 Cấu hình TTS | Text-to-Speech

### pyttsx3 (mặc định)
- ✅ Offline
- ✅ Nhanh
- ⚠️ Giọng robot

```bash
python -m translator_mini.main --mode assistant
```

### Google TTS
- ✅ Giọng tự nhiên
- ⚠️ Cần internet
- ⚠️ Chậm hơn một chút

```bash
python -m translator_mini.main --mode assistant --gtts
```

---

## 🛠️ Troubleshooting

### "No API key found"
```bash
# Kiểm tra file
cat api_key.txt

# Tạo lại
echo "sk-or-v1-xxxxx" > api_key.txt
```

### "Could not understand audio"
- Nói rõ ràng hơn
- Kiểm tra microphone
- Giảm tiếng ồn

### "Microphone error"
- Kiểm tra microphone được kết nối
- Thử chọn microphone khác: `--mic-index N`
- Windows: cho phép app truy cập microphone

### Voice không phát
- Kiểm tra loa/tai nghe
- Thử `--gtts` nếu pyttsx3 không hoạt động

---

## 📁 Cấu trúc file | File Structure

```
translator_mini/
├── main.py              # Entry point
├── openrouter_client.py # OpenRouter API
├── voice_assistant.py   # Voice/Text Assistant
├── speech_to_text.py    # Voice input
├── text_to_speech.py    # Voice output
├── api_key.txt          # Your API key (private)
└── requirements.txt     # Dependencies
```

---

## 💡 Tips

1. **Bắt đầu với text mode** để test API trước khi dùng voice
2. **Dùng `--gtts`** để có giọng nói tự nhiên hơn
3. **Model `gpt-4o-mini`** là lựa chọn tốt nhất về giá/chất lượng
4. **Nói "thoát" hoặc "quit"** để kết thúc voice assistant
5. **Lịch sử hội thoại** được giữ lại, AI nhớ context trước đó

---

## 📝 Change Log

- **v2.0** - Thêm Voice Assistant với OpenRouter AI
- **v1.0** - Translator EN→VI cơ bản

# ARCHITECTURE & FLOW (Cập nhật Gemini mặc định)

## Tổng quan nhanh
- Các chế độ chính: `voice` (dịch giọng), `text` (dịch văn bản), `assistant` (AI voice song ngữ), `assistant-text` (AI chat văn bản), `chat` (test API thuần).
- Mặc định nhà cung cấp AI: `gemini` (Google direct, không qua OpenRouter). Mặc định model: `gemini-flash` → ánh xạ `gemini-flash-latest` (free).
- Có thể chuyển sang OpenRouter bằng `--provider openrouter` + `--model ...` nếu cần model khác (GPT-4o, Claude, Llama…).
- TTS mặc định dùng gTTS + pygame (tiếng Việt tự nhiên), fallback pyttsx3 offline. STT dùng SpeechRecognition + Google Web Speech.

## Bản đồ nhanh (đọc 1 phút)
- Dịch thuần: EN → VI. Không giữ lịch sử. Nguồn AI: Google Translate (free) qua deep-translator.
- AI Assistant: giữ lịch sử, song ngữ, lệnh "dịch ..." trả bản dịch VI. Nguồn AI: Gemini (default) hoặc OpenRouter.
- Khoá: `gemini_api_key.txt` / `GEMINI_API_KEY`; `api_key.txt` / `OPENROUTER_API_KEY`.
- Chạy nhanh:
   - `python -m translator_mini.main --mode text --voice-output`
   - `python -m translator_mini.main --mode assistant --provider gemini --model gemini-flash`
   - `python -m translator_mini.main --mode chat --provider gemini --model gemini-2-flash`

## So sánh 2 luồng chính
```
┌───────────── Translator (EN→VI) ─────────────┐   ┌─────────────── AI Assistant (song ngữ) ────────────────┐
│ Input: mic/text (EN)                          │   │ Input: mic/text (VI/EN)                               │
│ STT (nếu mic) → translate_en_to_vi            │   │ STT (auto vi→en fallback)                             │
│ Engine: Google Translate (deep-translator)    │   │ Engine: GeminiChatbot (default) / OpenRouterChatbot   │
│ Output: text + optional TTS                   │   │ Logic: history + lệnh "dịch ..." → trả bản dịch VI   │
└───────────────────────────────────────────────┘   │ Output: text + TTS (auto detect vi/en)                 │
                                                                              └─────────────────────────────────────────────────────────┘
```

## Sơ đồ nhanh theo provider (assistant/chat)
```
Input (VI/EN)
   ↓
speech_to_text (nếu mic)
   ↓
main.py → voice_assistant.py
   ↓
if --provider gemini:
      gemini_client.GeminiChatbot (model alias → id hợp lệ)
else if --provider openrouter:
      openrouter_client.OpenRouterChatbot (REST)
   ↓
text_to_speech (gTTS/pyttsx3)
```

## Thành phần chính
- `main.py`: entrypoint + argparse, định tuyến mode và provider.
- `speech_to_text.py`: thu âm, chuẩn hóa nhiễu, nhận dạng (vi/en hoặc auto) qua Google Web Speech.
- `translator.py`: EN→VI qua deep-translator (Google Translate free).
- `text_to_speech.py`: phát âm; ưu tiên gTTS (+pygame) nếu có, fallback pyttsx3; chọn voice tiếng Việt nếu khả dụng.
- `chatbot.py`: pipeline đơn giản EN→VI + (tùy chọn) TTS.
- `openrouter_client.py`: gọi OpenRouter chat completions, kèm alias model và các hàm dịch AI.
- `gemini_client.py`: gọi Google Gemini trực tiếp, alias model hợp lệ (flash/pro/2.0/2.5), giữ history giống OpenRouter client.
- `voice_assistant.py`: trợ lý song ngữ; factory chọn chatbot theo provider, auto detect tiếng Việt/Anh, lệnh “dịch …” buộc trả bản dịch tiếng Việt.

## Luồng dữ liệu theo chế độ

### 1) Translator Text (`--mode text`)
1. CLI nhận `--input` (tùy chọn) hoặc chờ nhập từ stdin.
2. `ChatbotTranslatorMini.respond_text()` gọi `translate_en_to_vi()` → Google Translate (deep-translator).
3. In kết quả. Nếu bật `--voice-output`, TTS phát qua gTTS (ưu tiên) hoặc pyttsx3.

### 2) Translator Voice (`--mode voice`)
1. `speech_to_text.listen_and_recognize()` thu âm (mic_index tùy chọn), chuẩn hóa nhiễu, nhận dạng `language_in` (mặc định en-US).
2. Văn bản tiếng Anh → `translate_en_to_vi()`.
3. In kết quả; nếu `--voice-output`, phát qua TTS. `--loop` cho phép chạy liên tục.

### 3) AI Voice Assistant (`--mode assistant`)
1. Khởi tạo `VoiceAssistant(provider, model)` với system prompt bắt lệnh “dịch …”.
2. `listen()` thu âm: nếu `--lang auto`, thử vi-VN rồi fallback en-US; timeout và phrase_time_limit được giới hạn để tránh treo.
3. Ngữ cảnh: chatbot giữ history (tối đa 20 message). Với Gemini dùng `GeminiChatbot`, với OpenRouter dùng `OpenRouterChatbot`.
4. `think()` gọi model qua provider đã chọn; trả về tiếng Việt theo prompt mặc định.
5. `speak_response()` phát âm thanh; tự dò ngôn ngữ kết quả (vi/en) để chọn giọng.
6. Vòng lặp đến khi người dùng nói “thoát/quit/bye…”.

### 4) AI Text Assistant (`--mode assistant-text`)
1. Nhập từ bàn phím, hỗ trợ lệnh `reset`, `voice on/off`.
2. Chat qua chatbot tương ứng provider; giữ history.
3. Nếu `--no-speak` tắt TTS; mặc định phát giọng gTTS.

### 5) Chat API Test (`--mode chat`)
1. Giao tiếp text trực tiếp với provider đã chọn (mặc định Gemini) để debug model/KEY.

## Định tuyến provider & model
- `--provider gemini` (default): dùng `gemini_client.GeminiChatbot`; alias model:
  - `gemini-flash` → `gemini-flash-latest` (free, nhanh).
  - `gemini-pro` → `gemini-pro-latest`.
  - `gemini-2-flash`, `gemini-2-flash-lite`, `gemini-2.5-flash`, `gemini-2.5-pro` (đều direct, tránh 404).
- `--provider openrouter`: dùng `openrouter_client.OpenRouterChatbot`; alias model (ví dụ): `free`, `gpt-4o-mini`, `claude-sonnet`, `llama-70b`, `gemini-flash` (qua OpenRouter, khác endpoint).
- `--list-models` in ra alias + id thực cho cả hai provider.

## Quản lý khóa
- Gemini: đọc `gemini_api_key.txt` (cùng thư mục) hoặc biến môi trường `GEMINI_API_KEY`.
- OpenRouter: đọc `api_key.txt` hoặc biến `OPENROUTER_API_KEY`.
- Nếu thiếu KEY: in cảnh báo và bỏ qua yêu cầu.

## Sai lỗi & fallback
- STT: timeout/không nghe được → trả None, vòng lặp tiếp tục; catch microphone error để không crash.
- TTS: nếu gTTS/pygame lỗi → fallback pyttsx3; nếu cả hai lỗi chỉ in cảnh báo.
- Gemini/OpenRouter request lỗi hoặc 404 model → log lỗi, không ghi vào history để tránh lệch ngữ cảnh.
- Voice assistant: lệnh thoát (“quit/exit/bye/thoát/…”), lệnh reset trong text mode để xóa history.

## Sơ đồ rút gọn
```
User (mic/text)
   │
   ▼
main.py (argparse, route mode/provider)
   │
   ├─ Translator modes → translator.py (EN→VI via Google) → text_to_speech.py (optional)
   │
   └─ Assistant modes → voice_assistant.py
          ├─ speech_to_text.py (auto vi/en)
          ├─ chatbot provider:
          │     • GeminiChatbot (google-generativeai)
          │     • OpenRouterChatbot (REST)
          └─ text_to_speech.py (gTTS/pyttsx3)
```

## Tham số chính khi chạy
- `--mode voice|text|assistant|assistant-text|chat`
- `--provider gemini|openrouter` (mặc định gemini)
- `--model gemini-flash` (alias), đổi tùy nhu cầu
- `--voice-output` (dịch thường), `--gtts/--no-gtts`, `--no-speak` (assistant-text)
- `--mic-index`, `--lang auto|vi|en`, `--loop`, `--tts-rate`

## Ghi chú triển khai
- Gemini direct: tránh lỗi 404 bằng alias hợp lệ; free tier đủ cho flash/pro cơ bản.
- Nếu gặp 429 với model cao cấp: chuyển `gemini-flash` hoặc `gemini-2-flash-lite`.
- Dùng gTTS khi cần tiếng Việt tự nhiên; nếu không có mạng, bật `--no-gtts` để dùng pyttsx3 offline.

---

## Luồng chi tiết (như file cũ nhưng cập nhật Gemini)

### Translator Text (EN→VI)
```
User gõ "Hello"
   ↓
main.py (parse args)
   ↓
chatbot.ChatbotTranslatorMini.respond_text()
   ↓
translator.translate_en_to_vi()  → Google Translate (deep-translator)
   ↓
In ra "Xin chào"  + (nếu --voice-output) text_to_speech.speak()
```

### Translator Voice (mic)
```
Mic audio
   ↓
speech_to_text.listen_and_recognize(language_in=en-US default)
   ↓ (fail → báo và loop tiếp)
Chuỗi EN
   ↓
translate_en_to_vi() → Google Translate
   ↓
In tiếng Việt + (nếu bật) TTS gTTS/pyttsx3
```

### AI Voice Assistant (song ngữ, lệnh "dịch ...")
```
Mic audio
   ↓
listen(): vi-VN trước, nếu auto mà fail → thử en-US
   ↓
Chuỗi user_input (vi/en)
   ↓
think():
   • Provider=gemini → GeminiChatbot.chat(messages+history)
   • Provider=openrouter → OpenRouterChatbot.chat(...)
   • System prompt bắt lệnh "dịch ..." trả về bản dịch VI
   ↓
AI response (thường tiếng Việt)
   ↓
speak_response(): detect_language(response) → TTS gTTS/pyttsx3
   ↓
Loop đến khi user nói quit/thoát
```

### AI Text Assistant
```
User nhập text (stdin)
   ↓
TextAssistant.chat() → chatbot provider (giữ history)
   ↓
Hiển thị; nếu speak_output=True → TTS theo ngôn ngữ phản hồi
   ↓
Lệnh: reset (xóa history), voice on/off, quit
```

### Chat API Test
```
CLI → interactive_chat() theo provider
   ↓
Gọi trực tiếp Gemini/OpenRouter để kiểm tra KEY/model
```

---

## Kiến trúc triển khai (tóm tắt)

### Windows + Docker Desktop (dev nhanh)
```
Windows Host
   └─ Docker Desktop (WSL2 VM)
          └─ translator-mini:latest
                  ├─ Python 3.10 + deps (SpeechRecognition, gTTS, pygame, deep-translator…)
                  ├─ App code (main, voice_assistant, gemini_client, openrouter_client…)
                  └─ Hạn chế: không truy cập mic/speaker host → chỉ test text mode
```

### Orange Pi / Linux native hoặc Docker ARM64 (production)
```
Orange Pi (ARM64) + USB Mic + Speaker
   └─ Docker Engine (native ARM64)
          └─ translator-mini:latest --device /dev/snd --group-add audio
                  ├─ Full /dev/snd → STT + TTS hoạt động
                  ├─ Giọng gTTS/pyttsx3 hoạt động
                  └─ Chạy 24/7 (khuyến nghị kèm systemd hoặc restart policy)
```

---

## User journey nhanh
```
Dev test text: docker run ... --mode text → kiểm tra dịch EN→VI
Dev test voice: python -m translator_mini.main --mode voice --voice-output --loop
AI assistant: python -m translator_mini.main --mode assistant --provider gemini --model gemini-flash
Prod (Orange Pi): docker run --device /dev/snd ... --mode assistant --provider gemini
```

---

## So sánh triển khai (rút gọn)
```
┌──────────────────┬───────────────────────┬───────────────────────┐
│ Môi trường       │ Khả năng              │ Dùng cho              │
├──────────────────┼───────────────────────┼───────────────────────┤
│ Docker Desktop   │ Text OK, Voice ❌      │ Dev logic, nhanh gọn  │
│ (Windows)        │                       │                       │
├──────────────────┼───────────────────────┼───────────────────────┤
│ Native Python    │ Text/Voice ✅          │ Demo, kiểm thử full   │
│ (Windows/Linux)  │                       │                       │
├──────────────────┼───────────────────────┼───────────────────────┤
│ Orange Pi Docker │ Text/Voice ✅ (ARM64)  │ Production 24/7       │
└──────────────────┴───────────────────────┴───────────────────────┘
```

---

## Hiệu năng & lưu ý (ngắn)
- STT Google Web Speech: ~1-2s cho mẫu 5s; phụ thuộc mạng.
- Dịch deep-translator: <1s; TTS gTTS: <1s câu ngắn.
- Voice vòng lặp: ~3-5s end-to-end (nghe → nhận dạng → dịch/chat → phát).
- Nếu pygame/gTTS kẹt: đã có reset mixer mỗi lượt; vẫn lỗi → fallback pyttsx3.

---

## Ví dụ end-to-end (chi tiết từng bước + thư viện)

### 1) Luồng Voice Translator (EN→VI)
1. Thu âm đầu vào
   - Module: `speech_to_text.listen_and_recognize(mic_index, language_in="en-US")`
   - Thư viện: `SpeechRecognition` + `PyAudio`
   - Xử lý: calibrate nhiễu (`adjust_for_ambient_noise`), ghi âm (`listen`); gửi tới Google Web Speech API (`recognize_google`).
   - Kết quả: chuỗi tiếng Anh, ví dụ: `"Hello, how are you?"` (hoặc `None` nếu không nhận được).

2. Dịch EN→VI
   - Module: `translator.translate_en_to_vi(text)`
   - Thư viện: `deep_translator.GoogleTranslator`
   - Xử lý: gọi dịch với `source="en"`, `target="vi"` qua endpoint miễn phí của Google Translate.
   - Kết quả: chuỗi tiếng Việt, ví dụ: `"Xin chào, bạn khỏe không?"` (hoặc `None` nếu lỗi mạng).

3. Phát giọng (tùy chọn `--voice-output`)
   - Module: `text_to_speech.speak(text, use_gtts=True, rate=tts_rate)`
   - Thư viện: ưu tiên `gTTS` + `pygame` (phát file mp3 tạm); fallback `pyttsx3` (offline).
   - Xử lý: gTTS tạo file âm thanh → pygame phát; nếu lỗi, dùng pyttsx3 chọn voice Việt nếu có.
   - Kết quả: loa phát câu tiếng Việt; terminal in trạng thái thành công/thất bại.

4. Hiển thị kết quả
   - Module: `main.run_voice()` in `EN` đã nghe và `VI` đã dịch.
   - Kết quả: người dùng thấy text trên màn hình và nghe âm thanh.

### 2) Luồng AI Voice Assistant (song ngữ + lệnh "dịch ...")
1. Thu âm đầu vào
   - Module: `voice_assistant.VoiceAssistant.listen()`
   - Thư viện: `SpeechRecognition` + `PyAudio`
   - Xử lý: nếu `--lang auto` → thử `vi-VN` trước, nếu không có kết quả → thử `en-US`.
   - Kết quả: chuỗi người dùng (VI hoặc EN), ví dụ: `"dịch I love you"`.

2. Suy nghĩ/Chat AI
   - Module: `voice_assistant.VoiceAssistant.think(user_input)`
   - Provider: mặc định `gemini` → `gemini_client.GeminiChatbot` (giữ history); hoặc `openrouter_client.OpenRouterChatbot` nếu chọn `--provider openrouter`.
   - Thư viện: `google-generativeai` (Gemini) hoặc REST `requests` (OpenRouter API v1 chat completions).
   - Xử lý: gộp `system_prompt` (có quy tắc lệnh "dịch ...") + history + `user_input` → gửi lên model alias hợp lệ (`gemini-flash-latest`, v.v.).
   - Kết quả: phản hồi AI (thường tiếng Việt), ví dụ: `"Tôi yêu bạn."`.

3. Phát giọng phản hồi
   - Module: `voice_assistant.VoiceAssistant.speak_response(text, language="auto")`
   - Thư viện: `gTTS` + `pygame` hoặc `pyttsx3`.
   - Xử lý: tự dò ngôn ngữ bằng `detect_language()` để chọn `lang` phù hợp; phát âm thanh như trên.
   - Kết quả: loa phát câu trả lời của AI.

4. Vòng lặp hội thoại
   - Module: `voice_assistant.VoiceAssistant.run()`
   - Xử lý: tiếp tục các lượt; các lệnh `quit/thoát` → kết thúc; có thể `reset` ở text assistant để xóa history.
   - Kết quả: trải nghiệm hội thoại liên tục song ngữ.

### 3) Luồng AI Text Assistant (không mic)
1. Nhập bàn phím → `TextAssistant.run()` đọc stdin.
2. Chat: `TextAssistant.chat(user_input)` → chatbot theo provider.
3. TTS: nếu bật `speak_output`, phát giọng phản hồi.
4. Lệnh: `reset`, `voice on/off`, `quit`.

### 4) Luồng Chat API Test (debug KEY/model)
1. `main.py --mode chat` → `interactive_chat()` của provider đã chọn.
2. Gõ/nhận phản hồi để xác minh khóa và model alias/id.

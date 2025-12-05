# 🎤 CẢI THIỆN VOICE MODE - HƯỚNG DẪN

## ⚠️ Vấn Đề Đã Sửa

### 1. Loop chỉ chạy 1 lần
**Nguyên nhân:** Lỗi trong error handling  
**Giải pháp:** ✅ Thêm try-except trong loop, không để crash

### 2. Giọng TTS khó nghe
**Nguyên nhân:** pyttsx3 trên Windows không có giọng Việt tốt  
**Giải pháp:** ✅ Thêm **gTTS (Google Text-to-Speech)** - giọng Việt chuẩn!

---

## 🚀 Cài Đặt Mới

### Cài packages mới
```powershell
pip install gtts pygame
```

Hoặc cài toàn bộ:
```powershell
pip install -r requirements.txt
```

---

## 🎯 Cách Sử Dụng Mới

### Option 1: Voice Loop KHÔNG có TTS (Chỉ text - Nhanh nhất)
```powershell
python -m translator_mini.main --mode voice --loop
```
**Kết quả:**
- 🎤 Nói tiếng Anh → Nhận text tiếng Việt
- ✅ Loop liên tục
- ✅ Không có giọng TTS (chỉ hiển thị text)
- ⚡ Nhanh, rõ ràng

### Option 2: Voice Loop CÓ TTS (gTTS - Giọng tốt!)
```powershell
python -m translator_mini.main --mode voice --loop --voice-output
```
**Kết quả:**
- 🎤 Nói tiếng Anh → Nhận text + giọng tiếng Việt
- ✅ Dùng **gTTS** (Google TTS) - giọng chuẩn!
- ✅ Loop liên tục
- 🔊 Giọng Việt tự nhiên, rõ ràng

### Option 3: Điều chỉnh tốc độ TTS (nếu cần)
```powershell
python -m translator_mini.main --mode voice --loop --voice-output --tts-rate 120
```
- `--tts-rate 140`: Default (vừa phải)
- `--tts-rate 120`: Chậm hơn (rõ hơn)
- `--tts-rate 160`: Nhanh hơn

**Lưu ý:** `--tts-rate` chỉ áp dụng cho pyttsx3 (fallback). gTTS không dùng parameter này.

---

## 🎨 Giao Diện Mới

### Output cải thiện
```
[Main] 🎙️ Voice mode (continuous loop).
[Main] Speak English and I'll translate to Vietnamese.
[Main] Press Ctrl+C to stop.

[Main] --- Turn 1 ---
[STT] Calibrating for ambient noise…
[STT] Listening… Speak now.
[STT] Recognizing…
[STT] Heard: hello how are you
[Main] 🎤 Heard: hello how are you
[Main] 🇻🇳 Vietnamese: Xin chào bạn khỏe không

[Main] 👂 Listening again...

[Main] --- Turn 2 ---
[STT] Calibrating for ambient noise…
[STT] Listening… Speak now.
...
```

### Khi dừng (Ctrl+C)
```
^C
[Main] 🛑 Stopped after 5 turns.
```

---

## 🔊 So Sánh TTS

| TTS Engine | Quality | Speed | Internet | Windows |
|------------|---------|-------|----------|---------|
| **gTTS** (mới) | ⭐⭐⭐⭐⭐ Excellent | Medium | Required | ✅ |
| **pyttsx3** (cũ) | ⭐⭐ Poor | Fast | Offline | ✅ |

### gTTS (Google Text-to-Speech) - KHUYẾN NGHỊ
- ✅ Giọng Việt chuẩn, tự nhiên
- ✅ Phát âm đúng dấu, ngữ điệu
- ✅ Dễ nghe, rõ ràng
- ⚠️ Cần internet (gọi Google API)
- ⚠️ Hơi chậm (1-2s để generate audio)

### pyttsx3 (Fallback)
- ⚠️ Giọng máy móc, khó nghe
- ⚠️ Phát âm tiếng Việt không chuẩn
- ✅ Offline, không cần internet
- ✅ Nhanh

---

## 🛠️ Technical Changes

### 1. main.py
**Cải thiện:**
- ✅ Try-except trong `one_turn()` → loop không crash
- ✅ Thêm emoji và formatting rõ ràng
- ✅ Đếm số lượng turns
- ✅ Error recovery tốt hơn

**Thay đổi:**
```python
# Trước
print(f"[Main] EN: {text}")
print(f"[Main] VI: {vi}")

# Sau
print(f"[Main] 🎤 Heard: {text}")
print(f"[Main] 🇻🇳 Vietnamese: {vi}")
print()  # Dòng trống cho dễ đọc
```

### 2. text_to_speech.py
**Tính năng mới:**
- ✅ Thêm `speak_gtts()` - Google TTS
- ✅ Thêm `speak_pyttsx3()` - fallback
- ✅ Auto-fallback: gTTS fail → pyttsx3
- ✅ Pygame mixer cho audio playback
- ✅ Temporary file cleanup

**API mới:**
```python
speak(text, use_gtts=True)  # Prefer gTTS
speak(text, use_gtts=False) # Force pyttsx3
```

### 3. requirements.txt
**Thêm:**
```
gTTS>=2.3.0      # Google Text-to-Speech
pygame>=2.5.0    # Audio playback
```

---

## 📊 Performance

### Text Mode (No TTS)
```
Latency: ~2-3 seconds
- Listen: 1-2s
- STT: 0.5-1s
- Translate: 0.3-0.5s
- Display: instant
```

### Voice Mode (gTTS)
```
Latency: ~4-6 seconds
- Listen: 1-2s
- STT: 0.5-1s
- Translate: 0.3-0.5s
- gTTS generate: 1-2s
- Play audio: 1-2s
```

### Voice Mode (pyttsx3)
```
Latency: ~3-4 seconds
- Listen: 1-2s
- STT: 0.5-1s
- Translate: 0.3-0.5s
- pyttsx3 speak: 0.5-1s
```

---

## 🧪 Test Commands

### Test loop nhiều lần
```powershell
# Nói 5 câu khác nhau để test
python -m translator_mini.main --mode voice --loop --voice-output

# Test cases:
# 1. "Hello"
# 2. "How are you"
# 3. "Good morning"
# 4. "Thank you"
# 5. "See you later"
```

### Test TTS quality
```powershell
# Text mode với TTS để nghe giọng
python -m translator_mini.main --mode text --voice-output --input "Xin chào, tôi là chatbot dịch thuật"
```

### Test error recovery
```powershell
# Nói rất nhỏ hoặc không nói → xem có crash không
python -m translator_mini.main --mode voice --loop
# (Không nói gì, chờ timeout → should continue loop)
```

---

## 🐛 Troubleshooting

### Issue: "gTTS not available"
```
[TTS] gTTS not available. Install with: pip install gtts pygame
[TTS] Falling back to pyttsx3 (voice quality may be poor)
```
**Fix:**
```powershell
pip install gtts pygame
```

### Issue: "pygame mixer init failed"
**Nguyên nhân:** Không có audio output device  
**Fix:** Kiểm tra speaker/headphone đã cắm chưa

### Issue: Loop vẫn chỉ chạy 1 lần
**Kiểm tra:**
1. Có error message nào không?
2. Có crash không?
3. Thử thêm `--voice-output` để xem

**Debug:**
```powershell
# Chạy với Python trực tiếp xem full error
python -m translator_mini.main --mode voice --loop
```

### Issue: Giọng vẫn khó nghe
**Nếu dùng gTTS:**
- Kiểm tra internet connection
- Google TTS có thể bị rate limit → chờ vài giây

**Nếu fallback pyttsx3:**
- Đây là giới hạn của pyttsx3
- Cài gTTS để cải thiện

---

## 🎓 Usage Examples

### Example 1: Học từ vựng
```powershell
python -m translator_mini.main --mode voice --loop --voice-output

# Nói từng từ:
"Apple" → "Quả táo"
"Book" → "Cuốn sách"
"Computer" → "Máy tính"
```

### Example 2: Dịch câu dài
```powershell
python -m translator_mini.main --mode voice --loop

# Nói câu dài:
"I want to learn Vietnamese language because it's very interesting"
→ "Tôi muốn học tiếng Việt vì nó rất thú vị"
```

### Example 3: Test nhanh không TTS
```powershell
python -m translator_mini.main --mode voice --loop

# Chỉ nhìn text, không nghe audio
# → Nhanh hơn, dễ copy-paste
```

---

## ✅ Checklist

Sau khi update:
- [ ] Cài gTTS và pygame: `pip install gtts pygame`
- [ ] Test text mode: `python -m translator_mini.main --mode text --input "Hello"`
- [ ] Test voice loop (no TTS): `python -m translator_mini.main --mode voice --loop`
- [ ] Test voice loop (with TTS): `python -m translator_mini.main --mode voice --loop --voice-output`
- [ ] Kiểm tra giọng Việt có rõ hơn không
- [ ] Test loop chạy ít nhất 3-5 lần

---

## 🎯 Recommended Usage

**Cho học tập / testing:**
```powershell
python -m translator_mini.main --mode voice --loop --voice-output
```
- ✅ Có audio feedback (gTTS)
- ✅ Loop liên tục
- ✅ Học được cách phát âm

**Cho dịch nhanh:**
```powershell
python -m translator_mini.main --mode voice --loop
```
- ✅ Chỉ text, không audio
- ✅ Nhanh hơn
- ✅ Dễ copy kết quả

**Cho demo:**
```powershell
python -m translator_mini.main --mode voice --voice-output
```
- ✅ Single turn (không loop)
- ✅ Có audio
- ✅ Trình diễn cho người khác xem

---

**Updated:** December 5, 2025  
**Version:** 2.0 với gTTS support

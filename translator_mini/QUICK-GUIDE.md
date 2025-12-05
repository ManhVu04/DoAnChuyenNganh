# 🎉 HƯỚNG DẪN SỬ DỤNG NHANH

## ✅ Đã Test Thành Công

### Docker Desktop Windows
```powershell
# Build
cd x:\DoanChuyenNganh\translator_mini
docker build -t translator-mini .

# Test
docker run --rm translator-mini python3 -m translator_mini.test_docker
# Result: 4/5 tests PASS ✅

# Dịch một câu
docker run --rm translator-mini python3 -m translator_mini.main --mode text --input "Hello, how are you?"
# Output: Xin chào, bạn khỏe không? ✅
```

## 🚀 Các Cách Sử Dụng

### 1. Text Mode trên Docker (✅ Đã Test)
**Tốt nhất để:** Test logic, development

```powershell
# Interactive
docker run -it --rm translator-mini python3 -m translator_mini.main --mode text

# One-shot
docker run --rm translator-mini python3 -m translator_mini.main --mode text --input "Your text here"
```

**Kết quả:**
- ✅ Translation: WORKS
- ✅ Chatbot logic: WORKS  
- ❌ Microphone: KHÔNG WORK (do Docker VM)
- ❌ Speaker: KHÔNG WORK (do Docker VM)

### 2. Python Trực Tiếp trên Windows (⚠️ Chưa Test)
**Tốt nhất để:** Full testing với voice I/O

```powershell
# Cài dependencies
pip install -r requirements.txt

# Chạy với voice
python -m translator_mini.main --mode voice --voice-output --loop
```

**Kết quả mong đợi:**
- ✅ Translation: WORKS
- ✅ Chatbot logic: WORKS
- ✅ Microphone: WORKS (Windows API)
- ✅ Speaker: WORKS (Windows TTS)

### 3. Orange Pi Production (⚠️ Chưa Deploy)
**Tốt nhất để:** Production deployment

```bash
# Build
docker build -t translator-mini .

# Run với device access
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --mode voice --voice-output --loop
```

**Kết quả mong đợi:**
- ✅ Translation: WORKS
- ✅ Chatbot logic: WORKS
- ✅ Microphone: WORKS (ALSA device)
- ✅ Speaker: WORKS (ALSA + eSpeak)

## 📊 Test Results Summary

| Component | Docker Desktop | Python Native | Orange Pi |
|-----------|----------------|---------------|-----------|
| Imports | ✅ PASS | ⚠️ Not tested | ⚠️ Not tested |
| Translation | ✅ PASS | ⚠️ Not tested | ⚠️ Not tested |
| Chatbot | ✅ PASS | ⚠️ Not tested | ⚠️ Not tested |
| STT Module | ✅ PASS | ⚠️ Not tested | ⚠️ Not tested |
| TTS Module | ❌ FAIL (no audio) | ⚠️ Not tested | ⚠️ Not tested |
| Microphone | ❌ No device | ✅ Expected | ✅ Expected |
| Speaker | ❌ No device | ✅ Expected | ✅ Expected |

## 🎯 Recommended Workflow

```
┌─────────────────────────────────────────┐
│ STEP 1: Development                     │
│ Platform: Docker Desktop Windows        │
│ Mode: Text only                         │
│ Purpose: Test translation logic         │
│ Status: ✅ TESTED & WORKING            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ STEP 2: Integration Test (Optional)     │
│ Platform: Python native Windows         │
│ Mode: Voice input/output                │
│ Purpose: Test full user experience      │
│ Status: ⚠️ NOT TESTED YET              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ STEP 3: Production Deploy               │
│ Platform: Orange Pi + Docker            │
│ Mode: Voice input/output (24/7)         │
│ Purpose: Final deployment               │
│ Status: ⚠️ NOT DEPLOYED YET            │
└─────────────────────────────────────────┘
```

## 📖 Tài Liệu

- **README.md** - Overview & basic usage
- **README-DOCKER.md** - Docker Desktop chi tiết (Vietnamese) ⭐
- **WHY-NO-MIC.md** - Giải thích kỹ thuật về vấn đề microphone ⭐
- **ORANGE-PI-DEPLOY.md** - Hướng dẫn deploy production ⭐
- **quickstart.ps1** - PowerShell script để chạy nhanh

## ⚡ Quick Commands

```powershell
# Chạy quickstart script
.\quickstart.ps1

# Test translation
docker run --rm translator-mini python3 -m translator_mini.main --mode text --input "Good morning"

# Test suite
docker run --rm translator-mini python3 -m translator_mini.test_docker

# Interactive text mode
docker run -it --rm translator-mini python3 -m translator_mini.main --mode text

# Debug shell
docker run -it --rm translator-mini /bin/bash
```

## ⚠️ Lưu Ý Quan Trọng

1. **Docker Desktop KHÔNG THỂ access microphone**
   - Đây là giới hạn kiến trúc (VM isolation)
   - Không phải bug hay cấu hình sai
   - Xem WHY-NO-MIC.md để hiểu rõ

2. **Text mode works perfectly trên Docker**
   - Translation: ✅
   - Chatbot logic: ✅
   - Dùng để development/testing

3. **Voice mode cần Orange Pi hoặc native Python**
   - Orange Pi: Production (recommended)
   - Python native Windows: Testing
   - Docker WSL2: Không khuyến nghị (phức tạp)

## 🐛 Common Issues

### Issue 1: "Cannot find Dockerfile"
```powershell
# Đảm bảo ở đúng thư mục
cd x:\DoanChuyenNganh\translator_mini
docker build -t translator-mini .
```

### Issue 2: "test_docker.py not found"
```powershell
# Rebuild image (đã fix)
docker build --no-cache -t translator-mini .
```

### Issue 3: TTS test failed
```
✗ FAIL: TTS
```
**Đây là NORMAL!** Docker không có audio device. TTS vẫn work trên Orange Pi.

### Issue 4: No microphones detected
```
Detected microphones: 0
```
**Đây là EXPECTED!** Docker Desktop không access được Windows microphone.

## 📞 Next Steps

- [ ] **Deploy lên Orange Pi** (xem ORANGE-PI-DEPLOY.md)
- [ ] **Test Python native** trên Windows (nếu muốn test voice trước)
- [ ] **Setup systemd service** cho auto-start trên Orange Pi
- [ ] **Add offline STT** với Vosk (optional)
- [ ] **Add web interface** với Flask/FastAPI (optional)

## 💡 Pro Tips

1. Use `quickstart.ps1` để setup nhanh
2. Text mode trong Docker = test logic perfect
3. Không waste time với voice trong Docker Desktop
4. Deploy thẳng lên Orange Pi khi ready
5. Keep Docker image updated với `docker build`

---

**Status:** ✅ Docker setup COMPLETE & TESTED
**Next:** Deploy to Orange Pi or test native Python

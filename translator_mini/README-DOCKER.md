## 🐳 Hướng Dẫn Chạy Docker Desktop (Windows)

> ⚠️ **THÔNG BÁO QUAN TRỌNG:** Docker Desktop trên Windows **KHÔNG THỂ** truy cập microphone do kiến trúc VM. 
> Xem chi tiết: **[WHY-NO-MIC.md](WHY-NO-MIC.md)**
>
> **Giải pháp:**
> - ✅ Dùng **text mode** trong Docker để test logic
> - ✅ Chạy **Python trực tiếp** trên Windows để test voice
> - ✅ Deploy lên **Orange Pi** cho production với full voice

## Yêu Cầu
- ✅ **Docker Desktop for Windows** (phiên bản mới nhất)
- ✅ **WSL2** (Windows Subsystem for Linux 2) - khuyến nghị
- ✅ Kết nối Internet (để dịch và STT)

## Cài Đặt Docker Desktop

### Bước 1: Tải và cài Docker Desktop
```powershell
# Tải từ: https://www.docker.com/products/docker-desktop/
# Hoặc dùng winget (Windows 11)
winget install Docker.DockerDesktop
```

### Bước 2: Kích hoạt WSL2 (nếu chưa có)
```powershell
# Mở PowerShell với quyền Administrator
wsl --install
wsl --set-default-version 2
```

### Bước 3: Khởi động Docker Desktop
- Mở Docker Desktop từ Start Menu
- Đợi cho đến khi thấy "Docker Desktop is running"
- Kiểm tra: `docker --version` trong PowerShell

---

## 🚀 Chạy Chatbot với Docker

### Option 1: Chạy Text Mode (Khuyến nghị cho Docker Desktop)

#### Build image
```powershell
cd translator_mini
docker build -t translator-mini:latest .
```

#### Chạy text mode (gõ tiếng Anh, nhận tiếng Việt)
```powershell
docker run -it --rm translator-mini python3 main.py --mode text
```

#### Test một câu nhanh
```powershell
docker run --rm translator-mini python3 main.py --mode text --input "Hello, how are you?"
```

#### Chạy với voice output (TTS trong container)
```powershell
docker run -it --rm translator-mini python3 main.py --mode text --voice-output
```
**Lưu ý:** Audio output có thể không nghe được trên Windows Docker Desktop. Xem phần "Audio Support" bên dưới.

---

### Option 2: Dùng Docker Compose (Đơn giản hơn)

#### Khởi động với docker-compose
```powershell
    docker-compose up
```

#### Chạy interactive (text mode)
```powershell
docker-compose run --rm translator python3 main.py --mode text
```

#### Test hệ thống
```powershell
docker-compose run --rm translator python3 test_docker.py
```

---

## 🎤 Voice Mode (Microphone Input)

### ⚠️ Vấn Đề với Windows Docker Desktop

**Docker Desktop trên Windows KHÔNG THỂ truy cập trực tiếp microphone** vì:
1. Docker chạy trong Linux VM (WSL2 hoặc Hyper-V)
2. Microphone là USB/audio device của Windows host
3. Device passthrough từ Windows → VM → Container rất phức tạp và không ổn định

**Kết luận:** Voice mode (nhận giọng nói) **KHÔNG hoạt động** trên Windows Docker Desktop!

### ✅ Giải Pháp

#### Cách 1: Chạy Text Mode trên Docker Desktop (Đơn giản nhất)
```powershell
# Gõ text tiếng Anh → Nhận text tiếng Việt
docker run -it --rm translator-mini python3 main.py --mode text
```

#### Cách 2: Chạy trực tiếp trên Windows (Không dùng Docker)
```powershell
# Cài Python trực tiếp trên Windows
pip install -r requirements.txt
python main.py --mode voice --voice-output --loop
```
**Lưu ý:** Cần cài PyAudio trên Windows (hơi phức tạp).

#### Cách 3: Deploy lên Orange Pi / Raspberry Pi (Production)
```bash
# Trên Orange Pi/Ubuntu - MỚI CÓ microphone access!
docker build -t translator-mini .
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 main.py --mode voice --voice-output --loop
```

#### Cách 4: Thử trong WSL2 (Experimental - Không đảm bảo)
```bash
# Vào WSL2
wsl

# Di chuyển đến thư mục
cd /mnt/x/DoanChuyenNganh/translator_mini

# Build
docker build -t translator-mini .

# Thử passthrough (có thể không work)
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 main.py --list-mics
```
**Lưu ý:** WSL2 cũng không có direct access tới Windows microphone. Cần cấu hình PulseAudio phức tạp.

### 📊 So Sánh Các Cách

| Phương Pháp | Voice Input | Voice Output | Độ Phức Tạp | Khuyến Nghị |
|-------------|-------------|--------------|-------------|-------------|
| Docker Desktop (Text Mode) | ❌ | ❌ | ⭐ Dễ | ✅ Development |
| Python trực tiếp Windows | ✅ | ✅ | ⭐⭐ Trung bình | ✅ Full test |
| Orange Pi Docker | ✅ | ✅ | ⭐ Dễ | ✅ Production |
| WSL2 + Docker | ⚠️ Khó | ⚠️ Khó | ⭐⭐⭐ Phức tạp | ❌ Không khuyến nghị |

---

## 🔊 Audio Support trên Windows Docker Desktop

### Vấn đề
Docker Desktop trên Windows không hỗ trợ trực tiếp audio devices (speaker/microphone) vì chạy trong VM.

### Giải pháp

#### 1. **Text Mode** (Dễ nhất - Đã test OK)
```powershell
docker run -it --rm translator-mini python3 main.py --mode text
# Gõ tiếng Anh → Nhận tiếng Việt (text only)
```

#### 2. **PulseAudio Server** (Advanced)
Nếu bạn muốn audio output:
```powershell
# Cài PulseAudio trên Windows
# Tải từ: https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/

# Chạy PulseAudio server trên Windows
pulseaudio --load="module-native-protocol-tcp auth-anonymous=1"

# Chạy container với PULSE_SERVER
docker run -it --rm `
  -e PULSE_SERVER=host.docker.internal `
  translator-mini `
  python3 main.py --mode text --voice-output
```

#### 3. **Chạy trên Orange Pi** (Production)
Để đầy đủ voice input + output, chạy trực tiếp trên Orange Pi hoặc Raspberry Pi:
```bash
# Trên Orange Pi/Ubuntu
docker build -t translator-mini .
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 main.py --mode voice --voice-output --loop
```

---

## 🧪 Test Container

Chạy test suite để kiểm tra tất cả modules:
```powershell
docker run --rm translator-mini python3 test_docker.py
```

Kết quả mong đợi:
```
✓ PASS: Imports
✓ PASS: Translation
✓ PASS: TTS
✓ PASS: STT
✓ PASS: Chatbot

🎉 All tests passed! Container is ready to use.
```

---

## 📋 Các Lệnh Docker Hữu Ích

### Build lại image
```powershell
docker build --no-cache -t translator-mini .
```

### Xem logs
```powershell
docker logs chatbot_translator
```

### Vào shell container (debug)
```powershell
docker run -it --rm translator-mini /bin/bash
```

### Dọn dẹp
```powershell
# Xóa container đã dừng
docker container prune

# Xóa images không dùng
docker image prune

# Xóa tất cả (cẩn thận!)
docker system prune -a
```

---

## 🎯 Quick Start - Copy & Paste

**Cách nhanh nhất để test:**
```powershell
# 1. Chạy quickstart script
cd x:\DoanChuyenNganh\translator_mini
.\quickstart.ps1

# HOẶC manual:

# 2. Build
docker build -t translator-mini .

# 3. Test hệ thống
docker run --rm translator-mini python3 test_docker.py

# 4. Chạy text mode
docker run -it --rm translator-mini python3 main.py --mode text

# 5. Test một câu
docker run --rm translator-mini python3 main.py --mode text --input "Good morning"
```

---

## ⚙️ Tuỳ Chỉnh

### Build cho ARM64 (Orange Pi)
```powershell
# Build multi-platform image
docker buildx create --use
docker buildx build --platform linux/arm64,linux/amd64 -t translator-mini:multiarch .
```

### Thay đổi Python version
Sửa `Dockerfile` dòng đầu tiên:
```dockerfile
FROM python:3.11-slim  # hoặc 3.9, 3.10, 3.12
```

### Thêm dependencies
Thêm vào `requirements.txt`, sau đó rebuild:
```powershell
docker build --no-cache -t translator-mini .
```

---

## 🐛 Troubleshooting

### Lỗi: "Cannot connect to Docker daemon"
```powershell
# Đảm bảo Docker Desktop đang chạy
# Restart Docker Desktop từ system tray
```

### Lỗi: PyAudio build failed
```powershell
# Đã được fix trong Dockerfile với portaudio19-dev
# Nếu vẫn lỗi, build lại:
docker build --no-cache -t translator-mini .
```

### Lỗi: "No module named 'speech_recognition'"
```powershell
# Kiểm tra requirements.txt được copy đúng
docker run --rm translator-mini cat requirements.txt
```

### Container chạy rồi tắt ngay
```powershell
# Thêm -it để interactive
docker run -it --rm translator-mini python3 main.py --mode text
```

---

## 📚 Tài Liệu Thêm

- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- [WSL2 Setup Guide](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Docker Audio Solutions](https://github.com/mviereck/x11docker/wiki/Container-sound:-ALSA-or-Pulseaudio)

---

## ✅ Checklist Trước Khi Deploy lên Orange Pi

- [ ] Test text mode trong Docker Desktop Windows: OK
- [ ] Test translation với nhiều câu: OK
- [ ] Kiểm tra internet connection requirement: OK
- [ ] Transfer image sang Orange Pi: `docker save/load` hoặc Docker Hub
- [ ] Test voice mode trên Orange Pi với microphone thật
- [ ] Test voice output với speaker thật
- [ ] Setup systemd service (nếu cần tự động chạy)

---

## 💡 Tips

1. **Phát triển nhanh:** Dùng text mode trong Docker Desktop để test logic
2. **Test voice:** Dùng WSL2 hoặc chạy trực tiếp trên Orange Pi
3. **Debug:** Dùng `docker run -it --rm translator-mini /bin/bash` để vào shell
4. **Production:** Build image trên Windows, export và load trên Orange Pi

**Lưu ý quan trọng:** Docker Desktop trên Windows chủ yếu dùng để test code logic. Để test đầy đủ voice input/output, nên chạy trên Orange Pi hoặc Linux máy thật.

# 🍊 Hướng Dẫn Deploy lên Orange Pi

## Chuẩn Bị

### Hardware
- Orange Pi (hoặc Raspberry Pi) với Ubuntu/Armbian
- Microphone USB hoặc built-in
- Speaker hoặc headphone
- Kết nối internet (cho translation và STT)

### Software
- Ubuntu/Armbian đã cài đặt
- Docker đã cài (hướng dẫn bên dưới)
- SSH access (tuỳ chọn)

---

## Bước 1: Cài Docker trên Orange Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Thêm user vào docker group (để không cần sudo)
sudo usermod -aG docker $USER

# Logout và login lại để apply group
exit  # Sau đó SSH lại

# Kiểm tra
docker --version
docker run hello-world
```

---

## Bước 2: Transfer Docker Image

### Option A: Build trực tiếp trên Orange Pi (Khuyến nghị)

```bash
# Clone hoặc copy code vào Orange Pi
scp -r translator_mini/ orangepi@<IP>:/home/orangepi/

# SSH vào Orange Pi
ssh orangepi@<IP>

# Build image (có thể mất 5-10 phút)
cd translator_mini
docker build -t translator-mini .
```

### Option B: Save/Load từ Windows

```powershell
# Trên Windows: Save image
docker save translator-mini:latest | gzip > translator-mini.tar.gz

# Transfer qua SCP
scp translator-mini.tar.gz orangepi@<IP>:/home/orangepi/

# Trên Orange Pi: Load image
gunzip -c translator-mini.tar.gz | docker load
```

### Option C: Docker Hub (Nếu có account)

```powershell
# Trên Windows
docker tag translator-mini:latest <your-dockerhub>/translator-mini:latest
docker push <your-dockerhub>/translator-mini:latest

# Trên Orange Pi
docker pull <your-dockerhub>/translator-mini:latest
docker tag <your-dockerhub>/translator-mini:latest translator-mini:latest
```

---

## Bước 3: Test Audio Devices

```bash
# List microphones
arecord -l

# List speakers
aplay -l

# Test microphone (record 5s)
arecord -d 5 -f cd test.wav
aplay test.wav

# Thêm user vào audio group nếu cần
sudo usermod -aG audio $USER
```

---

## Bước 4: Chạy Container với Voice Mode

### Test microphone detection

```bash
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --list-mics
```

### Single turn (nói một lần)

```bash
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --mode voice --voice-output
```

### Continuous loop (liên tục lắng nghe)

```bash
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --mode voice --voice-output --loop
```

### Background mode với docker-compose

```bash
# Tạo docker-compose.yml cho Orange Pi
cat > docker-compose-orangepi.yml <<'EOF'
version: '3.8'

services:
  translator:
    image: translator-mini:latest
    container_name: chatbot_translator
    devices:
      - /dev/snd:/dev/snd
    group_add:
      - audio
    stdin_open: true
    tty: true
    restart: unless-stopped
    command: python3 -m translator_mini.main --mode voice --voice-output --loop
EOF

# Chạy
docker-compose -f docker-compose-orangepi.yml up -d

# Xem logs
docker logs -f chatbot_translator

# Stop
docker-compose -f docker-compose-orangepi.yml down
```

---

## Bước 5: Tối Ưu Performance

### Giảm TTS rate cho âm thanh rõ hơn
```bash
docker run -it --rm \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --mode voice --voice-output --tts-rate 140
```

### Chọn microphone cụ thể
```bash
# List mics trước
docker run -it --rm --device /dev/snd --group-add audio \
  translator-mini python3 -m translator_mini.main --list-mics

# Dùng mic index
docker run -it --rm --device /dev/snd --group-add audio \
  translator-mini python3 -m translator_mini.main --mode voice --mic-index 1 --voice-output
```

---

## Bước 6: Auto-start với systemd (Optional)

```bash
# Tạo systemd service
sudo nano /etc/systemd/system/translator.service
```

Nội dung:
```ini
[Unit]
Description=Chatbot Translator Mini
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=orangepi
WorkingDirectory=/home/orangepi/translator_mini
ExecStart=/usr/bin/docker run --rm --name translator \
  --device /dev/snd \
  --group-add audio \
  translator-mini \
  python3 -m translator_mini.main --mode voice --voice-output --loop
ExecStop=/usr/bin/docker stop translator
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable và start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable translator.service
sudo systemctl start translator.service

# Xem status
sudo systemctl status translator.service

# Xem logs
sudo journalctl -u translator.service -f
```

---

## Troubleshooting

### Lỗi: "No audio devices found"
```bash
# Kiểm tra ALSA
arecord -l
aplay -l

# Kiểm tra permissions
ls -la /dev/snd/

# Thêm user vào audio group
sudo usermod -aG audio $USER
newgrp audio
```

### Lỗi: "Permission denied" khi access /dev/snd
```bash
# Chạy với --privileged (temporary)
docker run -it --rm --privileged \
  translator-mini \
  python3 -m translator_mini.main --list-mics

# Hoặc set permissions
sudo chmod 666 /dev/snd/*
```

### Lỗi: TTS không có âm thanh
```bash
# Cài eSpeak Vietnamese voice
sudo apt install espeak espeak-data

# Test TTS trực tiếp
espeak -v vi "Xin chào"

# Kiểm tra volume
alsamixer
```

### Lỗi: STT không nhận giọng nói
```bash
# Test microphone trực tiếp
arecord -d 3 -f cd test.wav && aplay test.wav

# Tăng microphone gain
alsamixer
# Ấn F4 để chọn Capture, dùng arrow keys để tăng gain

# Trong Python, tăng energy_threshold
# Sửa speech_to_text.py: energy_threshold=500
```

### Container không start
```bash
# Xem logs chi tiết
docker logs chatbot_translator

# Check Docker status
docker ps -a

# Restart Docker
sudo systemctl restart docker
```

---

## Performance Tips

1. **Microphone Quality:** Dùng USB microphone tốt hơn built-in
2. **Network:** Kết nối ethernet ổn định hơn WiFi (cho API calls)
3. **CPU:** Orange Pi 3/4/5 performance tốt hơn Zero/One
4. **Cooling:** Thêm heatsink/fan nếu chạy 24/7
5. **Power:** Dùng power adapter 5V 3A trở lên

---

## Monitoring

### Resource usage
```bash
# CPU, memory
docker stats translator-mini

# Disk space
df -h

# Temperature (Orange Pi)
cat /sys/class/thermal/thermal_zone0/temp
```

### Logs
```bash
# Real-time logs
docker logs -f chatbot_translator

# Last 100 lines
docker logs --tail 100 chatbot_translator

# With timestamps
docker logs -t chatbot_translator
```

---

## Backup & Update

### Backup configuration
```bash
# Backup Docker image
docker save translator-mini:latest | gzip > backup-$(date +%Y%m%d).tar.gz

# Backup code
tar -czf code-backup-$(date +%Y%m%d).tar.gz translator_mini/
```

### Update application
```bash
# Pull new code
cd translator_mini
git pull  # hoặc scp code mới

# Rebuild image
docker build -t translator-mini .

# Restart container
docker-compose down
docker-compose up -d
```

---

## Next Steps

- [ ] Test với nhiều giọng nói khác nhau
- [ ] Thêm logging vào file
- [ ] Setup monitoring với Prometheus
- [ ] Thêm web interface (Flask/FastAPI)
- [ ] Support offline STT với Vosk
- [ ] Thêm nhiều ngôn ngữ (EN→VI→EN)

---

## Tài Liệu Thêm

- [Orange Pi Official Docs](http://www.orangepi.org/)
- [Docker on ARM](https://www.docker.com/blog/multi-arch-images/)
- [ALSA Configuration](https://wiki.archlinux.org/title/Advanced_Linux_Sound_Architecture)
- [eSpeak TTS](http://espeak.sourceforge.net/)

**🎉 Chúc bạn deploy thành công!**

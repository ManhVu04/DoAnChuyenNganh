# Chatbot Translator Mini (EN ➜ VI)

Lightweight Python project that runs on Orange Pi + Ubuntu (ARM), supporting:
- Voice input (microphone)
- Translate English ➜ Vietnamese
- Respond via text or optional speech (offline TTS)
- No GPU required, uses lightweight libraries

## Project Structure
```
translator_mini/
├─ main.py
├─ speech_to_text.py
├─ translator.py
├─ text_to_speech.py
├─ chatbot.py
├─ requirements.txt
└─ README.md
```

## Requirements
- Python 3.8+
- Internet connection for speech recognition and translation (default)
  - STT uses Google Web Speech (free tier). Optional offline STT can be added later with Vosk.
- For Orange Pi / Ubuntu (ARM):
  - PortAudio development headers for microphone access
  - eSpeak for offline TTS via `pyttsx3`

### Ubuntu/Orange Pi setup
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
  portaudio19-dev espeak alsa-utils
```

### Create venv and install Python packages
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If `pyaudio` fails to build, ensure `portaudio19-dev` is installed (as above), then try again.

### Optional: List microphones
```bash
python3 main.py --list-mics
```

## Usage

### Voice mode (default)
Listen from default mic, translate EN ➜ VI, print and optionally speak Vietnamese.
```bash
# Single turn, with spoken Vietnamese output
python3 main.py --mode voice --voice-output

# Continuous loop listening
python3 main.py --mode voice --voice-output --loop

# Choose a microphone index
python3 main.py --mode voice --mic-index 2 --voice-output
```

### Text mode
Type English and get Vietnamese output (optionally spoken).
```bash
python3 main.py --mode text
python3 main.py --mode text --voice-output

# One-shot translation
python3 main.py --mode text --input "Hello, how are you?" --voice-output
```

## Notes
- Speech Recognition uses Google's Web Speech API by default (no API key needed, but rate-limited).
- Translation uses `deep-translator` (Google). For heavy usage, consider your own translation service.
- TTS uses `pyttsx3` with system voices. On Ubuntu, eSpeak provides offline voices; if a Vietnamese voice is available, the app will prefer it.

## Offline STT (Optional, not enabled by default)
If you need fully offline speech-to-text, consider Vosk:
```bash
pip install vosk
# Download a small English model from: https://alphacephei.com/vosk/models
```
You can extend `speech_to_text.py` to use Vosk when available (not included in the minimal setup).

## Troubleshooting
- Microphone not detected: Check `arecord -l` and ALSA settings, ensure user is in `audio` group.
- PyAudio install errors: Confirm `portaudio19-dev` is installed before `pip install -r requirements.txt`.
- No Vietnamese TTS voice: `pyttsx3` falls back to default voice; install additional eSpeak voices if needed.

## 🐳 Docker Support
See **[README-DOCKER.md](README-DOCKER.md)** for complete Docker Desktop instructions:
- ✅ Run on Windows Docker Desktop (text mode) - **TESTED OK**
- ✅ Build multi-arch images (x86_64 + ARM64)
- ✅ Test suite for validation (4/5 tests pass)
- ⚠️ Voice mode requires Orange Pi deployment
- 📖 See [WHY-NO-MIC.md](WHY-NO-MIC.md) for technical explanation
- 🍊 See [ORANGE-PI-DEPLOY.md](ORANGE-PI-DEPLOY.md) for production deployment

**Quick test on Docker Desktop:**
```bash
docker build -t translator-mini .
docker run --rm translator-mini python3 main.py --mode text --input "Hello, how are you?"
# Output: Xin chào, bạn khỏe không?
```

## 🎯 Project Files

- `main.py` - CLI entry point
- `speech_to_text.py` - Microphone input & Google Speech Recognition
- `translator.py` - English → Vietnamese translation
- `text_to_speech.py` - Text-to-speech output (eSpeak)
- `chatbot.py` - Orchestrator combining all modules
- `test_docker.py` - Test suite for validation
- `requirements.txt` - Python dependencies
- `Dockerfile` - Multi-arch container definition
- `docker-compose.yml` - Quick deployment config
- `quickstart.ps1` - Windows PowerShell quick start script
- `README-DOCKER.md` - Docker Desktop guide (Vietnamese)
- `WHY-NO-MIC.md` - Technical explanation of microphone limitations
- `ORANGE-PI-DEPLOY.md` - Production deployment guide

## License
This project is provided as-is for educational purposes.

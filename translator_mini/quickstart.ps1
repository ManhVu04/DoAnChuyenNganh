# Quick Start Guide - Translator Mini Docker

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "   CHATBOT TRANSLATOR MINI - DOCKER QUICK START" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host "`n📌 THÔNG BÁO QUAN TRỌNG:" -ForegroundColor Red
Write-Host "   Docker Desktop trên Windows KHÔNG HỖ TRỢ microphone!" -ForegroundColor Red
Write-Host "   Chỉ có thể dùng TEXT MODE để test logic.`n" -ForegroundColor Yellow

Write-Host "🎯 CÁC CÁCH TEST:`n" -ForegroundColor Green

Write-Host "1️⃣  Text Mode (Gõ tiếng Anh → Nhận tiếng Việt)" -ForegroundColor Cyan
Write-Host "   docker run -it --rm translator-mini python3 main.py --mode text`n"

Write-Host "2️⃣  Test một câu nhanh" -ForegroundColor Cyan
Write-Host '   docker run --rm translator-mini python3 main.py --mode text --input "Hello, how are you?"' -ForegroundColor White
Write-Host ""

Write-Host "3️⃣  Chạy test suite (kiểm tra tất cả modules)" -ForegroundColor Cyan
Write-Host "   docker run --rm translator-mini python3 test_docker.py`n"

Write-Host "4️⃣  Vào shell container để debug" -ForegroundColor Cyan
Write-Host "   docker run -it --rm translator-mini /bin/bash`n"

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "=" * 49 -ForegroundColor Cyan

Write-Host "`n💡 ĐỂ DÙNG VOICE MODE (microphone + speaker):`n" -ForegroundColor Yellow

Write-Host "   Option A: Chạy trực tiếp trên Windows (không Docker)" -ForegroundColor White
Write-Host "            pip install -r requirements.txt"
Write-Host "            python main.py --mode voice --voice-output --loop`n"

Write-Host "   Option B: Deploy lên Orange Pi / Raspberry Pi" -ForegroundColor White
Write-Host "            docker run -it --rm --device /dev/snd \"
Write-Host "              --group-add audio translator-mini \"
Write-Host "              python3 main.py --mode voice --voice-output --loop`n"

Write-Host "📖 Chi tiết: Xem README-DOCKER.md`n" -ForegroundColor Magenta

# Kiểm tra Docker đang chạy
Write-Host "Checking Docker status..." -ForegroundColor Gray
try {
    docker info *>$null
    Write-Host "✅ Docker is running`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is NOT running. Please start Docker Desktop!`n" -ForegroundColor Red
    exit 1
}

# Kiểm tra image tồn tại
Write-Host "Checking translator-mini image..." -ForegroundColor Gray
$imageExists = docker images -q translator-mini
if ($imageExists) {
    Write-Host "✅ Image 'translator-mini' found`n" -ForegroundColor Green
    
    $choice = Read-Host "Do you want to run test suite now? (y/n)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "`n🧪 Running test suite...`n" -ForegroundColor Cyan
        docker run --rm translator-mini python3 test_docker.py
        
        Write-Host "`n`n🚀 Now try text mode:`n" -ForegroundColor Green
        Write-Host "   docker run -it --rm translator-mini python3 main.py --mode text`n" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Image 'translator-mini' not found`n" -ForegroundColor Yellow
    Write-Host "Build the image first:" -ForegroundColor White
    Write-Host "   docker build -t translator-mini .`n"
}

---
title: Kompres
emoji: 🎬
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: gpl-3.0
---

# Kompres

Kompresi video profesional untuk WhatsApp, Instagram, Telegram, dan platform media sosial lainnya.

## ✨ Fitur

### Kompresi & Encoding
- **Platform Presets** — Konfigurasi otomatis untuk WhatsApp, Instagram Feed, Instagram Story, Telegram, dan Email
- **Smart Compression** — Tentukan target ukuran file (MB), bitrate dihitung otomatis
- **H.264 High Profile** — Encoding efisien dengan kualitas visual tinggi
- **Kalibrasi Warna BT.709** — Warna akurat, tidak pucat saat dikirim lewat chat
- **Estimasi Ukuran** — Lihat perkiraan ukuran output sebelum kompresi dimulai

### Format Output
- **MP4 (H.264)** — Format universal, kompatibel semua platform
- **WebM (VP9)** — Format terbuka, efisien untuk web
- **GIF Animasi** — Konversi video ke GIF berkualitas tinggi dengan palettegen

### Editing
- **Video Trimming** — Potong video ke durasi yang diinginkan
- **Frame Rate Control** — Ubah FPS output (24, 30, 60)
- **Aspect Ratio Crop** — Crop otomatis ke 16:9, 9:16, 1:1, atau 4:3

### Perbandingan Hasil
- **Before/After Slider** — Geser untuk membandingkan frame asli dan hasil kompresi
- **Detail Teknis** — Tabel perbandingan resolusi, codec, FPS, dan bitrate
- **Progress Realtime** — Pantau encoding dengan kecepatan (x) dan estimasi waktu sisa

### User Experience
- **Session Recovery** — Refresh browser? File tidak hilang, klik "Lanjutkan" untuk melanjutkan
- **Dark/Light Mode** — Toggle tema di sidebar sesuai preferensi
- **Riwayat Kompresi** — Lihat 10 kompresi terakhir di sidebar
- **Drag & Drop** — Area upload yang besar dan responsif
- **Tanpa Watermark** — Hasil kompresi bersih tanpa tanda air
- **Format Input Lengkap** — Mendukung MP4, MOV, MKV, AVI, dan WebM

## 🚀 Cara Penggunaan

1. Upload video (drag & drop atau klik browse)
2. Pilih platform target atau atur parameter manual
3. Pilih format output (MP4/WebM/GIF)
4. *Opsional:* Aktifkan **Smart Compression** dan masukkan target ukuran
5. Klik **Mulai Kompresi**
6. Lihat perbandingan before/after
7. Download hasil

## 🛠️ Menjalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🐳 Menjalankan dengan Docker

```bash
docker build -t kompres .
docker run -p 7860:7860 kompres
```

## 📦 Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Frontend | Streamlit |
| Video Engine | FFmpeg (H.264, VP9, GIF palettegen) |
| Runtime | Python 3.11 |
| Deploy | Docker / Hugging Face Spaces |

## 📄 Lisensi

Proyek ini dilisensikan di bawah **GNU General Public License v3.0**.
Lihat file [LICENSE](LICENSE) untuk detail lengkap.

## 👤 Kredit

Dibuat dan dikembangkan oleh **Garden**.

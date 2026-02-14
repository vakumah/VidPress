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

## Fitur

- **Platform Presets** - Konfigurasi otomatis untuk WhatsApp, Instagram Feed, Instagram Story, Telegram, dan Email
- **H.264 High Profile** - Encoding efisien dengan kualitas visual tinggi
- **Kalibrasi Warna BT.709** - Warna akurat, tidak pucat saat dikirim lewat chat
- **Before/After** - Perbandingan video asli dan hasil kompresi secara berdampingan
- **Detail Perbandingan** - Tabel perbandingan resolusi, codec, FPS, dan bitrate
- **Video Trimming** - Potong video ke durasi yang diinginkan
- **Frame Rate Control** - Ubah FPS output (24, 30, 60)
- **Aspect Ratio Crop** - Crop otomatis ke 16:9, 9:16, 1:1, atau 4:3
- **Progress Bar** - Pantau progres encoding secara real-time
- **Tanpa Watermark** - Hasil kompresi bersih tanpa tanda air
- **Format Lengkap** - Mendukung MP4, MOV, MKV, AVI, dan WebM

## Cara Penggunaan

1. Upload video
2. Pilih platform target atau atur parameter manual
3. Klik **Mulai Kompresi**
4. Lihat perbandingan before/after
5. Download hasil

## Menjalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Menjalankan dengan Docker

```bash
docker build -t kompres .
docker run -p 7860:7860 kompres
```

## Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Frontend | Streamlit |
| Engine   | FFmpeg (H.264 High Profile) |
| Runtime  | Python 3.11 |
| Deploy   | Docker / Hugging Face Spaces |

## Lisensi

Proyek ini dilisensikan di bawah **GNU General Public License v3.0**.
Lihat file [LICENSE](LICENSE) untuk detail lengkap.

## Kredit

Dibuat dan dikembangkan oleh **Garden**.

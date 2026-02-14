---
title: VidPress
emoji: 🎬
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: gpl-3.0
---

# VidPress

Kompresi & optimasi video profesional untuk WhatsApp, Instagram, Telegram, dan platform media sosial lainnya.

## Fitur

- **Platform Presets** — Konfigurasi otomatis untuk WhatsApp, Instagram Feed, Instagram Story/Reels, Telegram, dan Email
- **Kompresi H.264 High Profile** — Encoding efisien dengan kualitas visual tinggi
- **Kalibrasi Warna BT.709** — Warna akurat, tidak pucat saat dikirim lewat chat
- **Video Info** — Analisis metadata video lengkap (resolusi, codec, FPS, bitrate, durasi)
- **Video Trimming** — Potong video ke durasi yang diinginkan
- **Frame Rate Control** — Ubah FPS output (24, 30, 60)
- **Aspect Ratio Crop** — Crop otomatis ke 16:9, 9:16, 1:1, atau 4:3
- **Bitrate Limiting** — Kontrol ukuran file maksimal
- **Format Lengkap** — Mendukung MP4, MOV, MKV, AVI, dan WebM
- **Web Optimized** — FastStart flag untuk pemutaran cepat di browser dan mobile

## Cara Penggunaan

1. Upload video melalui antarmuka web
2. Pilih platform target atau atur parameter secara manual
3. (Opsional) Atur trimming, FPS, dan aspect ratio di Pengaturan Lanjutan
4. Klik **Mulai Kompresi**
5. Download hasil video

## Menjalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Menjalankan dengan Docker

```bash
docker build -t vidpress .
docker run -p 7860:7860 vidpress
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
Lihat file [LICENSE](../LICENSE) untuk detail lengkap.

## Kredit

Dibuat dan dikembangkan oleh **Garden**.

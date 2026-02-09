# 1. Gunakan Python versi ringan (Slim) sebagai basis
FROM python:3.9-slim

# 2. Update Linux & Install FFmpeg (Wajib untuk engine konversi)
# Kita juga install libsm6 dkk supaya library gambar/video lancar
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 3. Buat User Baru (Hugging Face mewajibkan ini demi keamanan, gak boleh run as Root)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 4. Tentukan folder kerja
WORKDIR $HOME/app

# 5. Copy requirements dulu (biar cache-nya jalan, install jadi cepet)
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 6. Copy sisa file aplikasi (app.py)
COPY --chown=user . .

# 7. Buka Port 7860 (Port standar Hugging Face)
EXPOSE 7860

# 8. Perintah untuk menjalankan aplikasi saat container nyala
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]

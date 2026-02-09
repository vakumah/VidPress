import streamlit as st
import ffmpeg
import os
import tempfile
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra Compressor WA Native", layout="centered")

st.title("🟢 WhatsApp Native Compressor")
st.caption("Menggunakan Codec H.264 agar tidak dikompres ulang (membengkak) oleh WhatsApp.")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio, target_res):
    try:
        # Input stream
        stream = ffmpeg.input(input_path)
        
        # Audio Settings
        if remove_audio:
            audio_settings = {'an': None}
        else:
            # AAC LC adalah standar WA. Mono 64k cukup.
            audio_settings = {'c:a': 'aac', 'b:a': '64k', 'ac': 1}

        # Video Settings (KUNCI RAHASIANYA DI SINI)
        video_settings = {
            'vcodec': 'libx264',    # GANTI KE H.264 (WA Friendly)
            'crf': crf_value,       # 23-28 adalah sweet spot H.264
            'preset': preset_speed, 
            'pix_fmt': 'yuv420p',   # WA Wajib YUV420P
            'movflags': '+faststart',
            'profile:v': 'main',    # Profile aman
            'level': '3.1'          # Level kompatibilitas HP lama
        }

        # Resize Logic (Opsional, tapi membantu agar tidak resize otomatis)
        # Jika user memilih 720p, kita paksa scale. -2 artinya "ikut rasio aspek"
        if target_res == "720p":
            stream = ffmpeg.filter(stream, 'scale', 'trunc(oh*a/2)*2', 720)
        elif target_res == "480p":
            stream = ffmpeg.filter(stream, 'scale', 'trunc(oh*a/2)*2', 480)

        stream = ffmpeg.output(
            stream, 
            output_path,
            **audio_settings,
            **video_settings
        )
        
        # Jalankan
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True, None
        
    except ffmpeg.Error as e:
        return False, e.stderr.decode('utf8')

# --- UI Interface ---
uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "mkv"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
    tfile.write(uploaded_file.read())
    input_video_path = tfile.name

    original_size = os.path.getsize(input_video_path) / (1024 * 1024)
    st.info(f"📁 Ukuran Asli: {original_size:.2f} MB")

    with st.expander("⚙️ Pengaturan WA", expanded=True):
        # CRF H.264 beda dengan H.265.
        # Range aman: 23 (Bening) - 30 (Burik). Default 26.
        crf = st.slider("Level Kompresi (CRF)", 20, 35, 26, help="Makin tinggi = Makin kecil & buram. 26-28 recommended.") 
        
        speed = st.select_slider("Speed", options=["ultrafast", "fast", "medium", "slow", "veryslow"], value="medium")
        
        # Pilihan Resolusi (PENTING)
        # Seringkali WA resize paksa kalau resolusi aneh (misal 1080p ke 720p).
        # Mending kita resize duluan biar kontrol di tangan kita.
        resolution = st.selectbox("Paksa Resolusi (Tinggi)", ["Original", "720p", "480p"], index=1, help="Pilih 720p agar pas dengan standar Status WA.")
        
        rm_audio = st.checkbox("Hapus Suara")

    if st.button("🚀 GAS KOMPRES"):
        output_video_path = input_video_path + "_wa_ready.mp4"
        
        with st.spinner('Memasak video agar disukai WhatsApp...'):
            start_time = time.time()
            success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio, resolution)
            end_time = time.time()
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            compression_ratio = ((original_size - final_size) / original_size) * 100
            
            st.success(f"✅ Selesai! Ukuran: {final_size:.2f} MB")
            
            st.video(output_video_path)
            
            with open(output_video_path, "rb") as file:
                st.download_button("⬇️ Download (Format WA)", file, file_name="video_wa_fix.mp4")
        else:
            st.error("❌ Error")
            st.code(error_log)
            
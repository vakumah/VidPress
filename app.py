import streamlit as st
import ffmpeg
import os
import tempfile
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra WA Compressor V4 (Color Fix)", layout="centered")

st.title("💎 WA Compressor V4: Color Fix")
st.caption("Fitur: Warna HD (Anti Pucat) + Kompresi H.264 High Profile + Audio Fix")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio, target_res):
    try:
        # 1. Input Stream
        in_file = ffmpeg.input(input_path)
        video_stream = in_file.video
        audio_stream = in_file.audio

        # 2. Resize Logic (Memaksa resolusi genap agar warna akurat)
        if target_res == "720p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 720)
        elif target_res == "480p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 480)
        else:
            # Tetap pastikan resolusi genap walau original (syarat H.264)
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2')

        # 3. Settingan Video ULTIMATE (Color & Size)
        video_settings = {
            'vcodec': 'libx264',
            'crf': crf_value,
            'preset': preset_speed,
            
            # --- BAGIAN PENTING UNTUK WARNA ---
            'pix_fmt': 'yuv420p',       # Format pixel wajib WA
            'colorspace': 'bt709',      # Standar warna HD (Biar gak pucat)
            'color_primaries': 'bt709', # Standar warna HD
            'color_trc': 'bt709',       # Gamma correction HD
            'color_range': 'tv',        # Range TV (16-235) agar hitam pekat, bukan abu-abu
            # ----------------------------------

            'movflags': '+faststart',   # Web optimized
            'profile:v': 'high',        # 'High' lebih hemat tempat daripada 'Main'
            'tune': 'film',             # Optimasi khusus video kamera (biar gak kotak-kotak)
        }

        # 4. Assembly Output
        if remove_audio:
            stream = ffmpeg.output(video_stream, output_path, **video_settings, an=None)
        else:
            audio_settings = {'c:a': 'aac', 'b:a': '64k', 'ac': 1}
            stream = ffmpeg.output(audio_stream, video_stream, output_path, **audio_settings, **video_settings)
        
        # 5. Jalankan
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

    with st.expander("⚙️ Kontrol Kualitas", expanded=True):
        # CRF kita geser sedikit. 28 sudah sangat kecil. 
        # Kalau mau ekstrim tapi bagus, coba 28.
        crf = st.slider("Level Kompresi (Makin Besar = Makin Kecil File)", 20, 32, 28) 
        speed = st.select_slider("Speed Engine", options=["fast", "medium", "slow", "veryslow"], value="medium")
        resolution = st.selectbox("Resolusi", ["720p (Rekomendasi WA)", "Original", "480p"], index=0)
        rm_audio = st.checkbox("Bisu (Hapus Suara)")

    if st.button("🚀 PROSES (COLOR FIX)"):
        output_video_path = input_video_path + "_final.mp4"
        
        with st.spinner('Mengkalibrasi warna dan memadatkan video...'):
            success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio, resolution)
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            st.success(f"✅ Selesai! Ukuran: {final_size:.2f} MB")
            st.video(output_video_path)
            with open(output_video_path, "rb") as file:
                st.download_button("⬇️ Download Hasil", file, file_name="wa_hd_color.mp4")
        else:
            st.error("❌ Gagal")
            st.code(error_log)
            
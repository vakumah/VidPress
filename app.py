import streamlit as st
import ffmpeg
import os
import tempfile
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra WA V7 (1MB Hunter)", layout="centered")

st.title("💎 WA Compressor V7: 1MB Hunter")
st.caption("Target: Di Bawah 1 MB. Metode: 540p + Audio 32k + High Compression")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio, target_res, crispy_mode):
    try:
        in_file = ffmpeg.input(input_path)
        video_stream = in_file.video
        audio_stream = in_file.audio

        # --- 1. RESIZE STRATEGI (540p is The Sweet Spot) ---
        # 540p (960x540) adalah 1/4 dari Full HD. Tajam di HP, ukuran super kecil.
        if target_res == "540p (Rekomendasi 1MB)":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 540, flags='lanczos')
        elif target_res == "720p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 720, flags='lanczos')
        elif target_res == "480p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 480, flags='lanczos')
        else:
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2', flags='lanczos')

        # --- 2. VISUAL POP (Versi Ringan) ---
        if crispy_mode:
            # Kita kurangi dikit sharpeningnya biar gak nambah size brutal
            # Contrast naik dikit biar enak dilihat
            video_stream = ffmpeg.filter(video_stream, 'eq', contrast=1.05, saturation=1.1)
            video_stream = ffmpeg.filter(video_stream, 'unsharp', 5, 5, 0.8, 5, 5, 0.0)

        # 3. Settingan Video (H.264 High Profile)
        video_settings = {
            'vcodec': 'libx264',
            'crf': crf_value,       
            'preset': preset_speed,
            'pix_fmt': 'yuv420p',       
            'colorspace': 'bt709',      
            'color_primaries': 'bt709', 
            'color_trc': 'bt709',       
            'color_range': 'tv',        
            'movflags': '+faststart',   
            'profile:v': 'high',        
        }

        # 4. Output Assembly (Audio HEBAT - Hemat Banget)
        if remove_audio:
            stream = ffmpeg.output(video_stream, output_path, **video_settings, an=None)
        else:
            # Audio 32k Mono (Cukup buat ngomong/musik status WA, hemat size parah)
            audio_settings = {'c:a': 'aac', 'b:a': '32k', 'ac': 1}
            stream = ffmpeg.output(audio_stream, video_stream, output_path, **audio_settings, **video_settings)
        
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

    with st.expander("⚙️ Settingan 1 MB", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # DEFAULT SAYA UBAH KE 30.
            # 30-32 adalah kunci under 1MB.
            crf = st.slider("Level Kompresi (30-32 untuk <1MB)", 24, 38, 30) 
            # Default ke 540p
            resolution = st.selectbox("Resolusi", ["540p (Rekomendasi 1MB)", "720p", "480p"], index=0)
        with col2:
            # Preset veryslow wajib biar engine kerja keras madetin file
            speed = st.select_slider("Speed", options=["fast", "medium", "slow", "veryslow"], value="veryslow")
            crispy = st.checkbox("✨ Mode Visual Pop", value=True)
            
        rm_audio = st.checkbox("Bisu")

    if st.button("🚀 RAMPOK SIZE (JADI KECIL)"):
        output_video_path = input_video_path + "_1mb.mp4"
        
        with st.spinner('Meresolusi ulang ke 540p dan memangkas bitrate...'):
            success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio, resolution, crispy)
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            st.success(f"✅ Selesai! Ukuran: {final_size:.2f} MB")
            
            # Peringatan kalau masih di atas 1MB
            if final_size > 1.0:
                st.warning("⚠️ Masih di atas 1MB? Coba naikkan Level Kompresi ke 33 atau 35.")
            else:
                st.balloons()
                
            st.video(output_video_path)
            with open(output_video_path, "rb") as file:
                st.download_button("⬇️ Download Kecil", file, file_name="wa_under_1mb.mp4")
        else:
            st.error("❌ Gagal")
            st.code(error_log)
            
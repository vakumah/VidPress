import streamlit as st
import ffmpeg
import os
import tempfile
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra WA V5.1 (Fix Error)", layout="centered")

st.title("💎 WA Compressor V5.1: The Magician")
st.caption("Fitur: Fake 4K (Sharpening) + Color Fix + Size Kecil + Syntax Fix")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio, target_res, crispy_mode):
    try:
        # 1. Input Stream
        in_file = ffmpeg.input(input_path)
        video_stream = in_file.video
        audio_stream = in_file.audio

        # 2. Resize Logic
        if target_res == "720p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 720)
        elif target_res == "480p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 480)
        else:
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2')

        # --- 3. MAGIC TRICK: UNSHARP MASK (Fake 4K) ---
        if crispy_mode:
            # FIX ERROR DISINI:
            # Kita pisah argumennya pakai koma, bukan string panjang.
            # Format: luma_x, luma_y, luma_amt, chroma_x, chroma_y, chroma_amt
            video_stream = ffmpeg.filter(video_stream, 'unsharp', 5, 5, 1.2, 5, 5, 0.0)

        # 4. Settingan Video
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
            'tune': 'film',             
        }

        # 5. Output
        if remove_audio:
            stream = ffmpeg.output(video_stream, output_path, **video_settings, an=None)
        else:
            audio_settings = {'c:a': 'aac', 'b:a': '64k', 'ac': 1}
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

    with st.expander("⚙️ Kontrol Engine", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # PENTING: Untuk Mode Crispy, CRF jangan terlalu besar biar ga noise
            crf = st.slider("Level Kompresi (26-28 Ideal)", 20, 32, 26) 
            resolution = st.selectbox("Resolusi", ["720p (WA Standard)", "Original"], index=0)
        with col2:
            speed = st.select_slider("Speed", options=["fast", "medium", "slow", "veryslow"], value="medium")
            # INI DIA TOMBOL AJAIBNYA
            crispy = st.checkbox("✨ Mode Crispy (Fake 4K)", value=True, help="Membuat video tajam seperti 4K walau resolusi rendah.")
            
        rm_audio = st.checkbox("Bisu")

    if st.button("🚀 BIKIN TAJAM & KECIL"):
        output_video_path = input_video_path + "_crispy.mp4"
        
        with st.spinner('Menambahkan bumbu penyedap pixel...'):
            success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio, resolution, crispy)
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            st.success(f"✅ Selesai! Ukuran: {final_size:.2f} MB")
            st.video(output_video_path)
            with open(output_video_path, "rb") as file:
                st.download_button("⬇️ Download Hasil Crispy", file, file_name="video_wa_crispy.mp4")
        else:
            st.error("❌ Gagal")
            st.code(error_log)
            
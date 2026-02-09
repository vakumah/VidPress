import streamlit as st
import ffmpeg
import os
import tempfile
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra Compressor WA Fix Audio", layout="centered")

st.title("🟢 WhatsApp Native Compressor (Audio Fix)")
st.caption("Versi Final: Ukuran Kecil + Anti Buram + Audio Aman.")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio, target_res):
    try:
        # 1. Ambil Stream Input
        in_file = ffmpeg.input(input_path)
        
        # Pisahkan jalur Video dan Audio
        video_stream = in_file.video
        audio_stream = in_file.audio

        # 2. Logika Resize (Hanya memproses Video)
        if target_res == "720p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 720)
        elif target_res == "480p":
            video_stream = ffmpeg.filter(video_stream, 'scale', 'trunc(oh*a/2)*2', 480)

        # 3. Settingan Video (H.264 WA Friendly)
        video_settings = {
            'vcodec': 'libx264',
            'crf': crf_value,
            'preset': preset_speed,
            'pix_fmt': 'yuv420p',
            'movflags': '+faststart',
            'profile:v': 'main',
        }

        # 4. Final Output Assembly
        if remove_audio:
            # Kalau user minta bisu, kita cuma output video_stream saja
            stream = ffmpeg.output(
                video_stream, 
                output_path, 
                **video_settings, 
                an=None # Perintah hapus audio
            )
        else:
            # Kalau ada suara, kita gabungkan kembali (Audio + Video)
            audio_settings = {'c:a': 'aac', 'b:a': '64k', 'ac': 1}
            
            stream = ffmpeg.output(
                audio_stream, # Masukkan audio
                video_stream, # Masukkan video yang sudah di-resize
                output_path,
                **audio_settings,
                **video_settings
            )
        
        # 5. Eksekusi
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True, None
        
    except ffmpeg.Error as e:
        # Error handling kalau input aslinya memang tidak ada suara
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
        crf = st.slider("Level Kompresi (CRF)", 20, 35, 26, help="26-28 paling pas buat WA.") 
        speed = st.select_slider("Speed", options=["ultrafast", "fast", "medium", "slow", "veryslow"], value="medium")
        
        # Pilih 720p biar WA seneng
        resolution = st.selectbox("Paksa Resolusi", ["Original", "720p", "480p"], index=1)
        
        # Pastikan ini JANGAN dicentang kalau mau ada suara
        rm_audio = st.checkbox("Hapus Suara (Bisu)")

    if st.button("🚀 GAS KOMPRES"):
        output_video_path = input_video_path + "_wa_ready.mp4"
        
        with st.spinner('Memasak video + Mengamankan audio...'):
            start_time = time.time()
            success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio, resolution)
            end_time = time.time()
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            st.success(f"✅ Selesai! Ukuran: {final_size:.2f} MB")
            
            st.video(output_video_path)
            
            with open(output_video_path, "rb") as file:
                st.download_button("⬇️ Download Video", file, file_name="video_wa_audio_fix.mp4")
        else:
            st.error("❌ Gagal!")
            st.warning("Tips: Jika video aslimu memang tidak ada suaranya (bisu), centang 'Hapus Suara' agar tidak error.")
            with st.expander("Lihat Log Error"):
                st.code(error_log)
                
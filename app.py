import streamlit as st
import ffmpeg
import os
import tempfile
import shutil

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Ultra Compressor Engine", layout="centered")

st.title("🔥 Ultra Video Compressor")
st.markdown("""
    Engine ini menggunakan algoritma **H.265 (HEVC)** dengan metode **CRF** untuk memeras ukuran file sekecil mungkin tanpa merusak detail visual secara brutal.
""")

# --- Fungsi Engine Kompresi ---
def compress_video(input_path, output_path, crf_value, preset_speed, remove_audio):
    """
    Core Logic: Menggunakan FFmpeg untuk kompresi cerdas.
    """
    try:
        # Input stream
        stream = ffmpeg.input(input_path)
        
        # Audio settings
        if remove_audio:
            audio_settings = {'an': None} # Hapus audio total
        else:
            # Kompres audio ke AAC 64k mono (sangat hemat tapi suara jelas)
            audio_settings = {'c:a': 'aac', 'b:a': '64k', 'ac': 1}

        # Video stream dengan H.265
        stream = ffmpeg.output(
            stream, 
            output_path,
            **audio_settings,
            vcodec='libx265',      # Codec H.265 (Super Hemat)
            crf=crf_value,         # Kualitas (Lower = Bagus, Higher = Jelek/Kecil)
            preset=preset_speed,   # Speed (Slower = Lebih kecil & Bagus)
            movflags='+faststart'  # Agar video langsung play (web optimized)
        )
        
        # Jalankan command (overwrite yes)
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return True, None
        
    except ffmpeg.Error as e:
        return False, e.stderr.decode('utf8')

# --- UI Interface ---

uploaded_file = st.file_uploader("Upload Video (MP4/MOV/MKV)", type=["mp4", "mov", "mkv", "avi"])

if uploaded_file is not None:
    # Simpan file upload ke temp
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    input_video_path = tfile.name

    # Tampilkan info file asli
    original_size = os.path.getsize(input_video_path) / (1024 * 1024)
    st.info(f"📁 Ukuran Asli: {original_size:.2f} MB")

    # --- Pengaturan Advanced (Engine Control) ---
    with st.expander("⚙️ Pengaturan Engine (Advanced)", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # CRF 28 adalah sweet spot (kecil banget tapi masih layak tonton di HP)
            # Rentang: 18 (Bagus) - 28 (Default) - 35 (Burik tapi super kecil)
            crf = st.slider("Level Kompresi (CRF)", 18, 40, 28, help="Makin besar angka, makin kecil file (tapi kualitas turun). 28-30 disarankan untuk WA.")
        
        with col2:
            # Preset 'veryslow' bikin file paling kecil tapi proses lama
            speed = st.select_slider("Mode Proses", options=["medium", "slow", "veryslow"], value="medium", help="Veryslow = File paling kecil & kualitas terbaik, tapi nunggunya lama.")

        rm_audio = st.checkbox("Hapus Suara (Bisu)", help="Centang ini kalau mau ukuran ekstrim kecil (misal cuma video meme/cctv).")

    # Tombol Eksekusi
    if st.button("🚀 MULAI KOMPRESI"):
        output_video_path = input_video_path + "_compressed.mp4"
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Sedang memanaskan engine FFmpeg...")
        
        # Proses Kompresi
        success, error_log = compress_video(input_video_path, output_video_path, crf, speed, rm_audio)
        
        progress_bar.progress(100)
        
        if success:
            final_size = os.path.getsize(output_video_path) / (1024 * 1024)
            compression_ratio = ((original_size - final_size) / original_size) * 100
            
            st.success("✅ Kompresi Selesai!")
            
            # Statistik
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("Ukuran Asli", f"{original_size:.2f} MB")
            col_res2.metric("Hasil Kompresi", f"{final_size:.2f} MB")
            col_res3.metric("Penghematan", f"{compression_ratio:.0f}%")
            
            # Video Player Hasil
            st.video(output_video_path)
            
            # Tombol Download
            with open(output_video_path, "rb") as file:
                btn = st.download_button(
                    label="⬇️ Download Video Kecil",
                    data=file,
                    file_name="video_super_kecil.mp4",
                    mime="video/mp4"
                )
        else:
            st.error("❌ Terjadi Kesalahan pada Engine")
            with st.expander("Lihat Log Error"):
                st.code(error_log)

        # Cleanup file temp
        # (Opsional: di production sebaiknya pakai cronjob atau logic cleanup otomatis)
        